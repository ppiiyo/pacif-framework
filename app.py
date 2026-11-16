"""Streamlit demo for PACIF — synthetic sessions only (no stored user data)."""
import streamlit as st
import numpy as np
import pandas as pd
from pacif_core import (
    AuditReporter,
    DriftDetector,
    estimate_alignment,
    __version__,
)

# 3.1 cardinality guard: N >= min_expected_cell_count * n_u * n_s
# With 4 labels per side and cell_count=3 → need N >= 48; default window 80.
_N_LABELS = 4
_MIN_CELL = 3.0

st.set_page_config(
    page_title=f"PACIF v{__version__} Demo",
    page_icon="🔬",
    layout="wide",
)

st.title(f"🔬 PACIF v{__version__}")
st.caption(
    "Measures statistical coupling between user behavior and system context — "
    "and whether that estimate is reliable."
)

st.info(
    "**Synthetic demo.** Each Run generates new random sessions in-browser. "
    "Nothing is loaded from disk or a database; numbers change every run.\n\n"
    f"Estimator guard: window must be large enough for "
    f"~{_N_LABELS}×{_N_LABELS} labels (N ≥ {_MIN_CELL * _N_LABELS * _N_LABELS:.0f})."
)

st.markdown(
    """
PACIF helps you detect **feedback loops**, **behavioral lock-in**, and **drift**
in recommendation systems using transparent, audit-friendly metrics.

> For exploration and audit workflows: is user action tightly coupled to system
> context, is the estimate trustworthy, and does that relationship shift over time?
"""
)

st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuration")
    st.caption(f"Package version: `{__version__}`")

    with st.form("analysis_form"):
        n_sessions = st.slider("Sample Size (Sessions)", 50, 500, 200)
        session_len = st.slider(
            "Window Size (Events)",
            min_value=50,
            max_value=300,
            value=100,
            help=f"Need ≥ {_MIN_CELL * _N_LABELS * _N_LABELS:.0f} events for "
            f"{_N_LABELS}×{_N_LABELS} categories (3.1 cardinality guard).",
        )
        seed = st.number_input(
            "Random seed (reproducible runs)",
            min_value=0,
            max_value=10_000,
            value=42,
            step=1,
        )
        submitted = st.form_submit_button("🚀 Run Analysis", use_container_width=True)

if submitted:
    with st.spinner("Analyzing behavioral patterns..."):
        rng = np.random.default_rng(int(seed))
        results = []
        detector = DriftDetector()
        progress_bar = st.progress(0)
        status_counts: dict = {}

        for i in range(n_sessions):
            # Coupled synthetic pair: context ≈ action with 20% noise
            ev = rng.integers(0, _N_LABELS, session_len)
            mask = rng.random(session_len) < 0.2
            ctx = np.copy(ev)
            n_flip = int(np.sum(mask))
            if n_flip > 0:
                ctx[mask] = rng.integers(0, _N_LABELS, size=n_flip)

            res = estimate_alignment(
                ev,
                ctx,
                max_events=None,
                min_expected_cell_count=_MIN_CELL,
                sample_seed=int(seed) + i,
            )
            res["id"] = i
            reason = res.get("reason") or res.get("status")
            status_counts[reason] = status_counts.get(reason, 0) + 1

            mi = res.get("mi_estimate")
            if mi is not None:
                drift_res = detector.update(float(mi))
                res["drift"] = drift_res.get("drift", False)
            else:
                res["drift"] = False

            results.append(res)
            progress_bar.progress((i + 1) / n_sessions)

        progress_bar.empty()

        df = pd.DataFrame([r for r in results if r.get("status") == "success"])

        if not df.empty:
            col1, col2, col3 = st.columns(3)

            mean_mi = float(df["mi_estimate"].mean())
            col1.metric(
                label="Signal Strength (Mean MI)",
                value=f"{mean_mi:.3f} nats",
                delta="High coupling" if mean_mi > 0.5 else "Normal",
            )

            rel_rate = float(df["reliable"].mean()) * 100
            col2.metric(
                label="Reliable Data Ratio",
                value=f"{rel_rate:.1f}%",
            )

            has_drift = bool(df["drift"].any())
            col3.metric(
                label="Drift Status",
                value="Detected ⚠️" if has_drift else "Stable ✅",
                delta="Change detected" if has_drift else None,
            )

            st.markdown("---")
            st.subheader("📊 Alignment Dynamics")
            st.markdown("MI estimate per synthetic session (seeded RNG).")
            chart_data = df.set_index("id")[["mi_estimate"]]
            st.line_chart(chart_data, height=300)

            st.markdown("### 📝 Interpretation")
            if mean_mi > 0.8:
                st.warning(
                    "⚠️ **Strong signal:** actions are closely associated with context. "
                    "Investigate lock-in risk (association ≠ causation)."
                )
            elif mean_mi < 0.1:
                st.info(
                    "ℹ️ **Weak signal:** coupling is small or the sample is too noisy."
                )
            else:
                st.success("✅ **Moderate signal:** typical personalization range.")

            if has_drift:
                st.error(
                    "📉 **Drift alert:** alignment signal shifted over the session index."
                )

            if rel_rate < 80:
                st.error(
                    f"⚠️ **Low reliability:** only {rel_rate:.1f}% of estimates pass CI gates. "
                    "Increase window size or sample size."
                )

            st.markdown("---")
            st.subheader("📋 Audit Summary")
            audit_yaml = AuditReporter.generate_report(
                results,
                context={
                    "demo": True,
                    "seed": int(seed),
                    "n_sessions": n_sessions,
                    "window": session_len,
                },
            )
            with st.expander("View Technical Audit Report (YAML)"):
                st.code(audit_yaml, language="yaml")
        else:
            st.error(
                "No successful estimates. "
                "Increase window size (cardinality guard) or check status breakdown below."
            )
            st.json(status_counts)

st.markdown("---")
st.markdown(
    f"""
<div style='text-align: center; color: gray;'>
    <p>PACIF v{__version__} | synthetic demo |
    <a href="https://github.com/ppiiyo/pacif-framework" target="_blank">GitHub</a> |
    DOI: 10.5281/zenodo.19902776</p>
    <p>Built for transparency, reproducibility, and algorithmic accountability.</p>
</div>
""",
    unsafe_allow_html=True,
)
