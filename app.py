import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Trader Regime Intelligence Terminal",
    layout="wide"
)

# ======================================================
# GLOBAL STYLES
# ======================================================
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
.metric-card {
    background-color: #111827;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #1f2937;
}
.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    margin-top: 1.5rem;
}
.section-sub {
    color: #9CA3AF;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "outputs" / "tables"

@st.cache_data
def load_data():
    risk = pd.read_csv(DATA_DIR / "risk_summary.csv")
    cluster = pd.read_csv(DATA_DIR / "cluster_summary.csv")
    full = pd.read_csv(DATA_DIR / "daily_metrics_full.csv")
    feat = pd.read_csv(DATA_DIR / "feature_importance.csv")
    return risk, cluster, full, feat

risk_summary, cluster_summary, daily_full, feature_importance = load_data()

# ======================================================
# SIDEBAR FILTER
# ======================================================
st.sidebar.title("🛠 Regime Controls")

regimes = daily_full["sentiment_group"].unique()
selected_regimes = st.sidebar.multiselect(
    "Select Market Regimes",
    regimes,
    default=list(regimes)
)

filtered_df = daily_full[daily_full["sentiment_group"].isin(selected_regimes)]

# ======================================================
# HEADER
# ======================================================
st.title("📊 Trader Sentiment & Regime Intelligence Terminal")
st.markdown(
    "Quant-grade behavioral diagnostics for regime-based risk, "
    "volatility expansion, and structural trader segmentation."
)

st.divider()

# ======================================================
# KPI PANEL
# ======================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    sharpe_proxy = filtered_df["daily_pnl"].mean() / filtered_df["daily_pnl"].std()
    st.metric("Sharpe Proxy", f"{sharpe_proxy:.2f}")
    st.caption("Mean / Std PnL")
    st.markdown('</div>', unsafe_allow_html=True)

with k2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    # Compute volatility directly from daily PnL
    vol_expansion = filtered_df["daily_pnl"].std()

    st.metric("PnL Volatility (Std Dev)", f"{vol_expansion:,.0f}")
    st.caption("Standard Deviation of Daily PnL")
    st.markdown('</div>', unsafe_allow_html=True)

with k3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Active Days", filtered_df.shape[0])
    st.caption("Filtered Observations")
    st.markdown('</div>', unsafe_allow_html=True)

with k4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    dominant = filtered_df["sentiment_group"].mode()[0]
    st.metric("Dominant Regime", dominant)
    st.caption("Most Frequent State")
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# REGIME PNL DISTRIBUTION
# ======================================================
st.markdown('<div class="section-header">📈 PnL Distribution by Regime</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Risk dispersion across emotional states</div>', unsafe_allow_html=True)

fig_box = px.box(
    filtered_df,
    x="sentiment_group",
    y="daily_pnl",
    color="sentiment_group",
    template="plotly_dark"
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

# ======================================================
# VOLATILITY DRIVERS
# ======================================================
st.markdown('<div class="section-header">🔬 Volatility Drivers</div>', unsafe_allow_html=True)

feature_importance = feature_importance.sort_values("importance")

fig_feat = px.bar(
    feature_importance,
    x="importance",
    y="feature",
    orientation="h",
    template="plotly_dark"
)

st.plotly_chart(fig_feat, use_container_width=True)

# ======================================================
# ARCHETYPE MAP
# ======================================================
st.markdown('<div class="section-header">🎯 Behavioral Archetype Mapping</div>', unsafe_allow_html=True)

fig_cluster = px.scatter(
    cluster_summary,
    x="avg_trade_size_usd",
    y="daily_trade_count",
    size="pnl_volatility",
    color="cluster",
    log_x=True,
    template="plotly_dark"
)

st.plotly_chart(fig_cluster, use_container_width=True, key="cluster_map")
st.markdown("""
<div style="
    background: linear-gradient(145deg, #0f172a, #0b1220);
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    margin-top: 18px;
">

<h3 style="margin-bottom: 10px;">📌 Structural Interpretation</h3>

<div style="display: flex; gap: 30px;">

<div style="flex:1;">
<b style="color:#22c55e;">Cluster 0 — Tactical Participants</b>
<ul>
<li>Moderate trade size</li>
<li>Higher trading frequency</li>
<li>Short-term reactive positioning</li>
<li>Sensitive to volatility expansion</li>
</ul>
</div>

<div style="flex:1;">
<b style="color:#3b82f6;">Cluster 1 — Selective Participants</b>
<ul>
<li>Lower activity</li>
<li>Moderate capital deployment</li>
<li>Discretionary trading behavior</li>
<li>Limited systemic influence</li>
</ul>
</div>

<div style="flex:1;">
<b style="color:#f59e0b;">Cluster 2 — High-Impact Capital</b>
<ul>
<li>Large average trade size</li>
<li>Elevated PnL volatility</li>
<li>Whale / institutional behavior</li>
<li>Dominant in regime transitions</li>
</ul>
</div>

</div>

<hr style="border:0.5px solid #1f2937; margin:15px 0;">

<h4>🧠 Strategic Implication</h4>

Performance dispersion is structurally regime-dependent.  
Volatility expansion disproportionately benefits high-frequency and large-capital clusters.

<b>Implication:</b> Regime-conditional allocation outperforms static exposure frameworks.

</div>
""", unsafe_allow_html=True)

# ======================================================
# REGIME TREND
# ======================================================
st.markdown('<div class="section-header">📊 Regime Volatility Trend</div>', unsafe_allow_html=True)

vol_trend = (
    filtered_df
    .groupby("date")["daily_pnl"]
    .std()
    .reset_index()
    .rename(columns={"daily_pnl": "volatility"})
)

# fig_vol = px.line(
#     vol_trend,
#     x="date",
#     y="volatility",   # ✅ CORRECT
#     template="plotly_dark"
# )
fig_vol = px.line(
    vol_trend,
    x="date",
    y="volatility",
    template="plotly_dark"
)

fig_vol.update_traces(
    line=dict(color="#22c55e", width=2.5)
)

fig_vol.update_layout(
    xaxis_title="Date",
    yaxis_title="Volatility (Std Dev of Daily PnL)",
    hovermode="x unified",
    plot_bgcolor="#0b1220",
    paper_bgcolor="#0b1220"
)

st.plotly_chart(fig_vol, use_container_width=True)


# ======================================================
# FOOTER
# ======================================================
st.success("✅ Regime Intelligence Generated Using Behavioral Finance & Quant Risk Framework")