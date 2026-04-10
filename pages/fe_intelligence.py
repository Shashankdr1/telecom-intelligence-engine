# pages/fe_intelligence.py
import streamlit as st
import pandas as pd
import datetime
import base64
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.fe_filter import (
    get_vendor_scorecard, get_fe_scorecard,
    get_vendor_trends, get_fe_alerts,
    get_fe_countries, get_fe_vendors
)
from engine.fe_scorer import get_fe_recommendation


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title            = "FE Intelligence · GCX × Prodapt",
    page_icon             = "🧑‍🔧",
    layout                = "wide",
    initial_sidebar_state = "expanded"
)


# ─────────────────────────────────────────────
# LOGO HELPER
# ─────────────────────────────────────────────

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            ext  = path.split(".")[-1]
            mime = "image/webp" if ext == "webp" else "image/png"
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    except Exception:
        return ""

BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gcx_b64     = img_to_base64(os.path.join(BASE, "assets", "GCX.webp"))
prodapt_b64 = img_to_base64(os.path.join(BASE, "assets", "Prodapt.png"))

gcx_img     = f'<img src="{gcx_b64}" class="navbar-logo-gcx" alt="GCX"/>'     if gcx_b64     else '<span style="color:white;font-weight:800;">GCX</span>'
prodapt_img = f'<img src="{prodapt_b64}" class="navbar-logo-prodapt" alt="Prodapt"/>' if prodapt_b64 else '<span style="color:#ff4444;font-weight:800;">Prodapt</span>'


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
.block-container { padding-top: 0.5rem !important; }

[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
}

.navbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #0a0f1e; padding: 1rem 2rem;
    border-radius: 12px; margin: 0.5rem 0 0 0;
    border: 1px solid #1e3a5f;
}
.navbar-left  { display: flex; align-items: center; gap: 20px; }
.navbar-logo-gcx     { height: 32px; object-fit: contain; }
.navbar-logo-prodapt { height: 28px; object-fit: contain; background: white; border-radius: 5px; padding: 2px 8px; }
.navbar-divider { width: 1px; height: 32px; background: #2a3f5f; }
.navbar-title { color: #e8f4fd; font-size: 1.05rem; font-weight: 600; }
.navbar-right { display: flex; align-items: center; gap: 8px; }
.navbar-badge {
    background: #1e3a5f; color: #7eb8e8;
    font-size: 0.72rem; font-weight: 600;
    padding: 0.25rem 0.75rem; border-radius: 20px;
    border: 1px solid #2a5a8f; text-transform: uppercase;
}

.hero {
    background: linear-gradient(135deg, #0a0f1e 0%, #1a0d2e 40%, #2d1b4e 100%);
    border-radius: 12px; padding: 2.5rem 2.5rem 2rem 2.5rem;
    margin: 1rem 0 1.5rem 0; border: 1px solid #2d1b4e;
    position: relative; overflow: hidden;
}
.hero::before {
    content: "🧑‍🔧"; position: absolute;
    right: 2rem; top: 50%; transform: translateY(-50%);
    font-size: 6rem; opacity: 0.07;
}
.hero-tag {
    display: inline-block; background: rgba(90,30,160,0.3);
    color: #b07ee8; font-size: 0.75rem; font-weight: 700;
    padding: 0.25rem 0.8rem; border-radius: 20px;
    border: 1px solid #6a3aaf; text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero h1 { color: #ffffff; font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.hero h1 span { color: #9d6ee8; }
.hero p  { color: #9a8abf; font-size: 0.95rem; margin: 0; line-height: 1.6; }
.hero-stats { display: flex; gap: 2rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #2d1b4e; }
.hero-stat-value { color: #9d6ee8; font-size: 1.4rem; font-weight: 800; }
.hero-stat-label { color: #7a6a9a; font-size: 0.75rem; text-transform: uppercase; }

.section-title {
    font-size: 1rem; font-weight: 700; color: #0d1f3c;
    border-left: 4px solid #7c3aed;
    padding-left: 0.7rem; margin: 1.5rem 0 1rem 0;
}

.rec-card { border-radius: 12px; padding: 1.3rem 1.5rem; margin-bottom: 0.8rem; border: 1px solid #e2e8f0; }
.rec-card.primary { background: linear-gradient(135deg,#f5f3ff,#ede9fe); border-left: 5px solid #7c3aed; }
.rec-card.backup  { background: linear-gradient(135deg,#eff6ff,#dbeafe); border-left: 5px solid #3b82f6; }
.rec-card .tag    { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.rec-card.primary .tag { color: #6d28d9; }
.rec-card.backup  .tag { color: #2563eb; }
.rec-card .name      { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.rec-card .sub       { font-size: 0.82rem; color: #64748b; margin-bottom: 0.4rem; }
.rec-card .score-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; }
.rec-card .score-num { font-size: 1.4rem; font-weight: 800; color: #0f172a; }
.rec-card.primary .score-bar-fill { height: 6px; background: #7c3aed; border-radius: 3px; }
.rec-card.backup  .score-bar-fill { height: 6px; background: #3b82f6; border-radius: 3px; }
.rec-card .score-bar-bg { flex: 1; height: 6px; background: #e2e8f0; border-radius: 3px; }
.rec-card .reasoning { font-size: 0.86rem; color: #475569; line-height: 1.6; }

.alert-card { border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; border-left: 5px solid; }
.alert-card.high   { background: #fff1f2; border-color: #f43f5e; }
.alert-card.medium { background: #fffbeb; border-color: #f59e0b; }
.alert-card.low    { background: #eff6ff; border-color: #3b82f6; }
.alert-card .ah { font-weight: 700; font-size: 0.88rem; margin-bottom: 0.3rem; }
.alert-card.high   .ah { color: #be123c; }
.alert-card.medium .ah { color: #b45309; }
.alert-card.low    .ah { color: #1d4ed8; }
.alert-card .ab { font-size: 0.83rem; color: #475569; line-height: 1.5; }

.metric-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1rem; text-align: center;
}
.metric-card .ml { font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-bottom: 0.3rem; }
.metric-card .mv { font-size: 1.8rem; font-weight: 800; color: #7c3aed; }

.insight-box {
    background: linear-gradient(135deg,#f5f3ff,#ede9fe);
    border: 1px solid #ddd6fe; border-radius: 10px;
    padding: 1.1rem 1.3rem; font-size: 0.9rem;
    color: #2e1065; line-height: 1.7; margin-bottom: 1rem;
}
.action-box {
    background: linear-gradient(135deg,#fffbeb,#fef3c7);
    border: 1px solid #fde68a; border-radius: 10px;
    padding: 1.1rem 1.3rem; font-size: 0.9rem;
    color: #78350f; line-height: 1.7;
}

.results-bar {
    background: #f5f3ff; border: 1px solid #ddd6fe;
    border-radius: 10px; padding: 0.9rem 1.4rem; margin-bottom: 1rem;
}
.pill { display: inline-block; padding: 0.25rem 0.8rem; border-radius: 20px; font-size: 0.78rem; font-weight: 600; margin: 0.2rem; }
.pill-purple { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
.pill-orange { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }

.colour-good { background-color: #bbf7d0; color: #14532d; }
.colour-bad  { background-color: #fecdd3; color: #881337; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────

st.markdown(f"""
<div class="navbar">
    <div class="navbar-left">
        {gcx_img}
        <div class="navbar-divider"></div>
        {prodapt_img}
        <div class="navbar-divider"></div>
        <span class="navbar-title">Field Engineer Intelligence Engine</span>
    </div>
    <div class="navbar-right">
        <span class="navbar-badge">🧑‍🔧 Field Ops</span>
        <span class="navbar-badge">🤖 AI Powered</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🧑‍🔧 FE Job Requirement")
    st.markdown("---")

    country      = st.selectbox("🌍 Country",    get_fe_countries())
    vendor       = st.selectbox("🏢 FE Vendor",  get_fe_vendors())

    

    st.markdown("")
    run_button = st.button("🔍 Analyse FE Performance", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("#### ℹ️ How it works")
    st.markdown("**1.** Select country & deadline")
    st.markdown("**2.** Click Analyse FE Performance")
    st.markdown("**3.** AI scores vendors & engineers")
    st.markdown("**4.** Review scorecards & alerts")
    st.markdown("---")
    st.caption("Data: 1,335 jobs · 3 vendors · 30 FEs · 10 countries")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def render_rec_card(card_type, label, name, sub, score, reasoning):
    icon  = "✅" if card_type == "primary" else "🔄"
    width = max(0, min(100, score))
    st.markdown(f"""
    <div class="rec-card {card_type}">
        <div class="tag">{icon} {label}</div>
        <div class="name">{name}</div>
        <div class="sub">{sub}</div>
        <div class="score-row">
            <span class="score-num">{score}</span>
            <span style="font-size:0.8rem;color:#94a3b8;">/100</span>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{width}%"></div>
            </div>
        </div>
        <div class="reasoning">{reasoning}</div>
    </div>
    """, unsafe_allow_html=True)


def render_alert_card(alert):
    sev  = alert["severity"].lower()
    icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    icon  = icons.get(sev, "⚪")
    st.markdown(f"""
    <div class="alert-card {sev}">
        <div class="ah">{icon} {alert['severity']} · Vendor: {alert['vendor']}</div>
        <div class="ab"><strong>Issue:</strong> {alert['issue']} &nbsp;|&nbsp; <strong>Actual:</strong> {alert['actual']} &nbsp;|&nbsp; <strong>Threshold:</strong> {alert['threshold']}</div>
    </div>
    """, unsafe_allow_html=True)


def colour_pct_good(val):
    return "background-color: #bbf7d0; color: #14532d" if val >= 70 else "background-color: #fecdd3; color: #881337"

def colour_duration(val):
    return "background-color: #bbf7d0; color: #14532d" if val <= 8 else "background-color: #fecdd3; color: #881337"

def colour_cost(val):
    if val <= 500:   return "background-color: #bbf7d0; color: #14532d"
    elif val <= 700: return "background-color: #fef08a; color: #713f12"
    else:            return "background-color: #fecdd3; color: #881337"


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

if run_button:

    st.markdown(f"""
    <div class="results-bar">
        <strong>📊 FE Analysis Results</strong> &nbsp;
        <span class="pill pill-purple">🌍 {country}</span>
        <span class="pill pill-purple">🏢 {vendor}</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 AI Recommendation",
        "📊 Vendor & FE Scorecards",
        "🚨 Risk Alerts",
        "📈 Trends",
    ])


    # ── TAB 1 — AI RECOMMENDATION ───────────────
    with tab1:
        with st.spinner("Analysing FE performance..."):
            result = get_fe_recommendation(country, expected_days)

        if "error" in result:
            st.error(result["error"])
        else:
            # Vendors
            st.markdown('<div class="section-title">🏢 Vendor Recommendation</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                pv = result["primary_vendor"]
                render_rec_card("primary", "Primary Vendor", pv["vendor"], "FE Vendor", pv["score"], pv["reasoning"])
            with col2:
                bv = result["backup_vendor"]
                render_rec_card("backup", "Backup Vendor", bv["vendor"], "FE Vendor", bv["score"], bv["reasoning"])

            # FEs
            st.markdown('<div class="section-title">🧑‍🔧 Field Engineer Recommendation</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3:
                pf = result["primary_fe"]
                render_rec_card("primary", "Primary FE", pf["fe_name"], f"Vendor: {pf['vendor']}", pf["score"], pf["reasoning"])
            with col4:
                bf = result["backup_fe"]
                render_rec_card("backup", "Backup FE", bf["fe_name"], f"Vendor: {bf['vendor']}", bf["score"], bf["reasoning"])

            # Cost insight
            st.markdown('<div class="section-title">💰 Cost Insight</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-box">{result["cost_insight"]}</div>', unsafe_allow_html=True)

            # Action plan
            st.markdown('<div class="section-title">📋 Action Plan</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="action-box">{result["action_plan"]}</div>', unsafe_allow_html=True)


    # ── TAB 2 — SCORECARDS ──────────────────────
    with tab2:
        # Vendor scorecard
        st.markdown('<div class="section-title">🏢 Vendor Scorecard</div>', unsafe_allow_html=True)
        vendor_df = get_vendor_scorecard(country if country != "All" else None)

        if vendor_df.empty:
            st.warning("No vendor data found.")
        else:
            display = vendor_df.rename(columns={
                "vendor"                 : "Vendor",
                "total_jobs"             : "Total Jobs",
                "closed_jobs"            : "Closed Jobs",
                "closure_rate_pct"       : "Closure Rate %",
                "task_acceptance_pct"    : "Task Acceptance %",
                "fe_closure_pct"         : "FE Closure %",
                "closer_measurement_pct" : "Closer Measurement %",
                "avg_duration_hrs"       : "Avg Duration (hrs)",
                "avg_cost_usd"           : "Avg Cost (USD)",
                "avg_cost_optimization"  : "Avg Saving (USD)",
                "total_saving_usd"       : "Total Saving (USD)",
            })
            styled = display.style\
                .map(colour_pct_good, subset=["Closure Rate %", "Task Acceptance %", "FE Closure %"])\
                .map(colour_duration, subset=["Avg Duration (hrs)"])\
                .map(colour_cost,     subset=["Avg Cost (USD)"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("---")

        # FE individual scorecard
        st.markdown('<div class="section-title">🧑‍🔧 Individual FE Scorecard</div>', unsafe_allow_html=True)
        fe_df = get_fe_scorecard(
            country if country != "All" else None,
            vendor  if vendor  != "All" else None
        )

        if fe_df.empty:
            st.warning("No FE data found for this selection.")
        else:
            display = fe_df.rename(columns={
                "fe_name"             : "FE Name",
                "vendor"              : "Vendor",
                "total_jobs"          : "Total Jobs",
                "closure_rate_pct"    : "Closure Rate %",
                "task_acceptance_pct" : "Task Acceptance %",
                "fe_closure_pct"      : "FE Closure %",
                "avg_duration_hrs"    : "Avg Duration (hrs)",
                "avg_cost_usd"        : "Avg Cost (USD)",
            })
            styled = display.style\
                .map(colour_pct_good, subset=["Closure Rate %", "Task Acceptance %", "FE Closure %"])\
                .map(colour_duration, subset=["Avg Duration (hrs)"])\
                .map(colour_cost,     subset=["Avg Cost (USD)"])
            st.dataframe(styled, use_container_width=True, hide_index=True)


    # ── TAB 3 — RISK ALERTS ─────────────────────
    with tab3:
        st.markdown('<div class="section-title">🚨 FE Vendor Risk Alerts</div>', unsafe_allow_html=True)
        alerts = get_fe_alerts(country if country != "All" else None)

        if not alerts:
            st.success("✅ No alerts — all vendors within acceptable thresholds.")
        else:
            high_c   = sum(1 for a in alerts if a["severity"] == "High")
            medium_c = sum(1 for a in alerts if a["severity"] == "Medium")
            low_c    = sum(1 for a in alerts if a["severity"] == "Low")

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><div class="ml">🔴 High</div><div class="mv" style="color:#f43f5e">{high_c}</div></div>',   unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><div class="ml">🟡 Medium</div><div class="mv" style="color:#f59e0b">{medium_c}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><div class="ml">🟢 Low</div><div class="mv" style="color:#3b82f6">{low_c}</div></div>',       unsafe_allow_html=True)

            st.markdown("")
            for alert in alerts:
                render_alert_card(alert)


    # ── TAB 4 — TRENDS ──────────────────────────
    with tab4:
        st.markdown('<div class="section-title">📈 Vendor Performance Trends</div>', unsafe_allow_html=True)
        st.caption("Month by month performance across all vendors.")

        trend_df = get_vendor_trends()

        if trend_df.empty:
            st.warning("No trend data available.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Closure Rate % — higher is better**")
                st.line_chart(
                    trend_df.pivot_table(index="month", columns="vendor", values="closure_rate_pct"),
                    use_container_width=True
                )
            with col2:
                st.markdown("**Task Acceptance % — higher is better**")
                st.line_chart(
                    trend_df.pivot_table(index="month", columns="vendor", values="task_acceptance_pct"),
                    use_container_width=True
                )

            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Total Jobs per Month**")
                st.line_chart(
                    trend_df.pivot_table(index="month", columns="vendor", values="total_jobs"),
                    use_container_width=True
                )
            with col4:
                st.markdown("**Average Cost (USD) — lower is better**")
                st.line_chart(
                    trend_df.pivot_table(index="month", columns="vendor", values="avg_cost_usd"),
                    use_container_width=True
                )


# ── LANDING ──────────────────────────────────
else:
    st.markdown("""
    <div class="hero">
        <div class="hero-tag">Field Engineer Intelligence</div>
        <h1>Smart FE Selection for<br><span>Telecom Field Operations</span></h1>
        <p>
            Analyse historical field engineer and vendor performance to recommend
            the best engineer for any job — backed by AI scoring, SLA analysis
            and cost intelligence.
        </p>
        <div class="hero-stats">
            <div><div class="hero-stat-value">1,335</div><div class="hero-stat-label">Jobs</div></div>
            <div><div class="hero-stat-value">3</div><div class="hero-stat-label">Vendors</div></div>
            <div><div class="hero-stat-value">30</div><div class="hero-stat-label">Engineers</div></div>
            <div><div class="hero-stat-value">10</div><div class="hero-stat-label">Countries</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.7rem;">🌍</div>
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;margin-bottom:0.4rem;">Step 1 — Select Job</div>
            <div style="font-size:0.83rem;color:#64748b;line-height:1.6;">Choose country, vendor filter and expected completion deadline from the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.7rem;">🤖</div>
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;margin-bottom:0.4rem;">Step 2 — Run Analysis</div>
            <div style="font-size:0.83rem;color:#64748b;line-height:1.6;">AI scores all vendors and individual FEs using historical job performance data.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.7rem;">📊</div>
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;margin-bottom:0.4rem;">Step 3 — Review Results</div>
            <div style="font-size:0.83rem;color:#64748b;line-height:1.6;">Review vendor scorecards, individual FE rankings, risk alerts and trend charts.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.info("💡 Use the **arrow (›)** on the top left to reopen the sidebar if it's hidden.")