import streamlit as st
import numpy as np
import pandas as pd
from pacif_core import estimate_alignment, DriftDetector, AuditReporter

# 1. Настройка страницы
st.set_page_config(
    page_title="PACIF v3.0 Demo",
    page_icon="🔬",
    layout="wide"
)

# 2. Hero Section (Заголовок)
st.title("🔬 PACIF v3.0")
st.caption("Measures how strongly an algorithm shapes user behavior — and whether that signal is reliable.")

st.markdown("""
PACIF helps you detect **feedback loops**, **behavioral lock-in**, and **drift** in recommendation systems 
using transparent, audit-friendly metrics.

> **This demo is for exploration and audit workflows.** It shows whether user actions are becoming 
too tightly coupled to system context, whether the result is statistically trustworthy, and 
whether that relationship changes over time.
""")

st.markdown("---")

# 3. Sidebar Controls (Панель настроек)
with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.form("analysis_form"):
        n_sessions = st.slider("Sample Size (Sessions)", 50, 500, 200)
        session_len = st.slider("Window Size (Events)", 30, 200, 60)
        
        threshold = st.selectbox(
            "Reliability Threshold",
            ["Strict (0.13 CI width)", "Medium (0.30 CI width)", "Relaxed (0.50 CI width)"],
            index=1
        )
        
        submitted = st.form_submit_button("🚀 Run Analysis", use_container_width=True)

# 4. Main Area (Результаты)
if submitted:
    with st.spinner('Analyzing behavioral patterns...'):
        
        # Симуляция данных
        results = []
        detector = DriftDetector()
        progress_bar = st.progress(0)
        
        for i in range(n_sessions):
            # Генерация событий (исправленная версия)
            ev = np.random.randint(0, 5, session_len)
            
            # Маска для случайного шума
            mask = np.random.random(session_len) < 0.2
            ctx = np.copy(ev)
            
            # Безопасное присвоение через маску
            if np.sum(mask) > 0:
                ctx[mask] = np.random.randint(0, 5, size=int(np.sum(mask)))
            
            # Оценка
            res = estimate_alignment(ev, ctx)
            res['id'] = i
            
            # Дрейф
            drift_res = detector.update(res.get('mi_estimate', 0))
            res['drift'] = drift_res.get('drift', False)
            
            results.append(res)
            progress_bar.progress((i + 1) / n_sessions)
            
        progress_bar.empty()

        # Фильтрация надежных данных
        df = pd.DataFrame([r for r in results if r['status'] == 'success'])
        
        if not df.empty:
            
            # --- Блок 1: KPI Карточки ---
            col1, col2, col3 = st.columns(3)
            
            # Сигнал (MI)
            mean_mi = df['mi_estimate'].mean()
            col1.metric(
                label="Signal Strength (Mean MI)", 
                value=f"{mean_mi:.3f} nats",
                delta="High coupling" if mean_mi > 0.5 else "Normal"
            )
            
            # Надежность
            rel_rate = df['reliable'].mean() * 100
            col2.metric(
                label="Reliable Data Ratio", 
                value=f"{rel_rate:.1f}%",
                delta_color="normal"
            )
            
            # Дрейф
            has_drift = df['drift'].any()
            col3.metric(
                label="Drift Status", 
                value="Detected ⚠️" if has_drift else "Stable ✅",
                delta="Change detected" if has_drift else None
            )

            st.markdown("---")

            # --- Блок 2: График ---
            st.subheader("📊 Alignment Dynamics")
            st.markdown("Visualizing how the signal strength changes over the session window.")
            
            chart_data = df.set_index('id')[['mi_estimate']]
            st.line_chart(chart_data, height=300)

            # --- Блок 3: Интерпретация (Human-readable) ---
            st.markdown("### 📝 Interpretation")
            
            if mean_mi > 0.8:
                st.warning("⚠️ **Strong Signal Detected:** Recommendations are very closely associated with user actions. Potential lock-in risk.")
            elif mean_mi < 0.1:
                st.info("ℹ️ **Weak Signal:** The relationship is small or data is too noisy to draw conclusions.")
            else:
                st.success("✅ **Moderate Signal:** Standard personalization level.")

            if has_drift:
                st.error("📉 **Drift Alert:** User behavior changed significantly over time. Re-calibration recommended.")
            
            if rel_rate < 80:
                st.error(f"⚠️ **Low Reliability:** Only {rel_rate:.1f}% of estimates are trustworthy. Increase window size or sample size.")

            st.markdown("---")

            # --- Блок 4: Footer & Audit ---
            st.subheader("📋 Audit Summary")
            
            audit_yaml = AuditReporter.generate_report(results)
            with st.expander("View Technical Audit Report (YAML)"):
                st.code(audit_yaml, language="yaml")

        else:
            st.error("No reliable data generated. Please try a larger sample size.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>PACIF v3.0 Framework | <a href="https://github.com/ppiyo/pacif-framework" target="_blank">GitHub Repo</a> | DOI: 10.5281/zenodo.19902776</p>
    <p>Built for transparency, reproducibility, and algorithmic accountability.</p>
</div>
""", unsafe_allow_html=True)

