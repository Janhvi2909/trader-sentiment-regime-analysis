import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

# ---------- THEME ----------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Trader Sentiment & Regime Intelligence Dashboard")
st.caption("Regime-based performance diagnostics, behavioral drivers, volatility modeling, and trader archetype segmentation.")

# ---------- LOAD DATA ----------
daily_metrics = pd.read_csv("outputs/daily_metrics_summary.csv")
risk_summary = pd.read_csv("outputs/risk_summary.csv")
cluster_summary = pd.read_csv("outputs/cluster_summary.csv")
feature_importance = pd.read_csv("outputs/feature_importance.csv")

# =====================================================
# 1️⃣ REGIME RISK SUMMARY
# =====================================================

st.markdown("## 1️⃣ Regime Risk & Performance Summary")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Risk Metrics by Sentiment")
    st.dataframe(risk_summary, use_container_width=True)

with col2:
    st.subheader("Risk-Adjusted Performance")

    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(
        data=risk_summary,
        x="sentiment_group",
        y="risk_adjusted_score",
        palette="Blues_d",
        ax=ax
    )
    ax.set_ylabel("Mean / Std")
    ax.set_xlabel("")
    ax.set_title("Risk-Adjusted Score by Regime")
    st.pyplot(fig)

# =====================================================
# 2️⃣ VOLATILITY PREDICTION DRIVERS
# =====================================================

st.markdown("---")
st.markdown("## 2️⃣ Volatility Prediction Drivers")

fig2, ax2 = plt.subplots(figsize=(7,4))

feature_importance = feature_importance.sort_values("importance", ascending=True)

sns.barplot(
    data=feature_importance,
    x="importance",
    y="feature",
    palette="viridis",
    ax=ax2
)

ax2.set_title("Feature Importance – Next-Day Volatility")
ax2.set_xlabel("Relative Importance")
ax2.set_ylabel("")
st.pyplot(fig2)

st.info("Insight: Trade size and frequency dominate volatility forecasting. Sentiment alone does not explain risk expansion.")

# =====================================================
# 3️⃣ TRADER ARCHETYPE SEGMENTATION
# =====================================================

st.markdown("---")
st.markdown("## 3️⃣ Trader Archetype Segmentation")

col3, col4 = st.columns([1.1, 1])

with col3:
    st.subheader("Cluster Summary")
    st.dataframe(cluster_summary, use_container_width=True)

with col4:
    st.subheader("Behavioral Positioning")

    fig3, ax3 = plt.subplots(figsize=(6,4))

    sns.scatterplot(
        data=cluster_summary,
        x="avg_trade_size_usd",
        y="daily_trade_count",
        hue="cluster",
        size="pnl_volatility",
        sizes=(200, 1500),
        palette="deep",
        alpha=0.85,
        ax=ax3
    )

    ax3.set_title("Archetype Mapping")
    ax3.set_xlabel("Average Trade Size (USD)")
    ax3.set_ylabel("Daily Trade Count")

    st.pyplot(fig3)

st.markdown("""
**Cluster Interpretation**

• **Cluster 0** → High-frequency, moderate-size traders  
• **Cluster 1** → Low-frequency, selective participants  
• **Cluster 2** → High-size, volatility-amplifying actors  

Distinct structural behavior across segments validates regime-conditional strategy allocation.
""")

# =====================================================
# 4️⃣ INTERACTIVE REGIME EXPLORER
# =====================================================

st.markdown("---")
st.markdown("## 4️⃣ Interactive Daily Regime Explorer")

uploaded_file = st.file_uploader("Upload daily_metrics_full.csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    sentiment_filter = st.selectbox(
        "Select Sentiment Regime",
        df["sentiment_group"].unique()
    )

    filtered = df[df["sentiment_group"] == sentiment_filter]

    st.metric(
        "Average Daily PnL",
        f"${filtered['daily_pnl'].mean():,.0f}"
    )

    st.metric(
        "Average Win Rate",
        f"{filtered['daily_win_rate'].mean():.2%}"
    )

    fig4, ax4 = plt.subplots(figsize=(7,4))
    sns.histplot(filtered["daily_pnl"], bins=30, kde=True, ax=ax4)
    ax4.set_title(f"PnL Distribution – {sentiment_filter}")
    st.pyplot(fig4)

else:
    st.warning("Upload daily_metrics_full.csv to enable dynamic exploration.")
