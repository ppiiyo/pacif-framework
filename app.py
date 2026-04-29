import streamlit as st, numpy as np, pandas as pd
from pacif_core import estimate_alignment, DriftDetector, AuditReporter

st.set_page_config(page_title="PACIF v3.0", layout="wide")
st.title("🔬 PACIF: Predictive Alignment Framework")

if st.button("🚀 Run Analysis"):
    n_sess, s_len = 200, 60
    progress = st.progress(0)
    results, detector = [], DriftDetector()
    
    for i in range(n_sess):
        ev = np.random.randint(0,5,s_len)
        ctx = np.copy(ev); ctx[np.random.random(s_len)<0.2] = np.random.randint(0,5,sum(np.random.random(s_len)<0.2))
        r = estimate_alignment(ev, ctx); r['id']=i; r['drift']=detector.update(r['mi_estimate'])['drift']
        results.append(r); progress.progress((i+1)/n_sess)
    
    df = pd.DataFrame([r for r in results if r['status']=='success'])
    if not df.empty:
        c1,c2,c3 = st.columns(3)
        c1.metric("Mean MI", f"{df['mi_estimate'].mean():.3f} nats")
        c2.metric("Reliable", f"{df['reliable'].mean()*100:.1f}%")
        c3.metric("Drift", "⚠️ Yes" if df['drift'].any() else "✅ No")
        st.bar_chart(df.set_index('id')['mi_estimate'])
        st.code(AuditReporter.generate_report(results), language="yaml")