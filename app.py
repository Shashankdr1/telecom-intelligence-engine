# app.py
import streamlit as st
import pandas as pd
import datetime
import base64
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers    import get_countries, get_service_types
from engine.filter    import filter_carriers, filter_suppliers, get_carrier_trends, get_supplier_trends
from engine.scorer    import get_recommendation
from engine.alerts    import get_all_alerts
from utils.pdf_export import generate_pdf


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title = "Carrier & Supplier Intelligence · GCX × Prodapt",
    page_icon  = "📡",
    layout     = "wide"
)


# ─────────────────────────────────────────────
# LOGO HELPER
# ─────────────────────────────────────────────

def img_to_base64(path):
    with open(path, "rb") as f:
        ext  = path.split(".")[-1].replace("webp", "webp").replace("png", "png")
        mime = "image/webp" if ext == "webp" else "image/png"
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

BASE  = os.path.dirname(os.path.abspath(__file__))
gcx_b64     = img_to_base64(os.path.join(BASE, "assets", "GCX.webp"))
prodapt_b64 = img_to_base64(os.path.join(BASE, "assets", "Prodapt.png"))


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>

/* ── Hide Streamlit default elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* ── Top navbar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0a0f1e;
    padding: 0.7rem 2rem;
    border-radius: 0 0 12px 12px;
    margin-bottom: 0;
    border-bottom: 2px solid #1e3a5f;
}
.navbar-left {
    display: flex;
    align-items: center;
    gap: 20px;
}
.navbar-logo {
    height: 36px;
    object-fit: contain;
}
.navbar-divider {
    width: 1px;
    height: 32px;
    background: #2a3f5f;
}
.navbar-title {
    color: #e8f4fd;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.navbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.navbar-badge {
    background: #1e3a5f;
    color: #7eb8e8;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    border: 1px solid #2a5a8f;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1f3c 40%, #1a3a6b 100%);
    border-radius: 12px;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    margin: 1rem 0 1.5rem 0;
    border: 1px solid #1e3a5f;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "📡";
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    opacity: 0.07;
}
.hero-tag {
    display: inline-block;
    background: rgba(30, 90, 160, 0.3);
    color: #7eb8e8;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    border: 1px solid #2a5a8f;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero h1 {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.hero h1 span { color: #4a9edd; }
.hero p {
    color: #7a9bbf;
    font-size: 0.95rem;
    margin: 0;
    max-width: 600px;
    line-height: 1.6;
}
.hero-stats {
    display: flex;
    gap: 2rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1e3a5f;
}
.hero-stat-value { color: #4a9edd; font-size: 1.4rem; font-weight: 800; }
.hero-stat-label { color: #5a7a9a; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Section title ── */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0d1f3c;
    border-left: 4px solid #1a6bbf;
    padding-left: 0.7rem;
    margin: 1.5rem 0 1rem 0;
    letter-spacing: 0.01em;
}

/* ── Results header ── */
.results-bar {
    background: #f0f6ff;
    border: 1px solid #c8dff5;
    border-radius: 10px;
    padding: 0.9rem 1.4rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.results-bar-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0d1f3c;
    margin-right: 0.5rem;
}
.pill {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.1rem;
}
.pill-blue   { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
.pill-green  { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.pill-orange { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }

/* ── Rec cards ── */
.rec-card {
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.8rem;
    border: 1px solid #e2e8f0;
    transition: box-shadow 0.2s;
}
.rec-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.rec-card.primary {
    background: linear-gradient(135deg, #f0fff4, #e6ffed);
    border-left: 5px solid #22c55e;
}
.rec-card.backup {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border-left: 5px solid #3b82f6;
}
.rec-card .tag {
    font-size: 0.7rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.rec-card.primary .tag { color: #16a34a; }
.rec-card.backup  .tag { color: #2563eb; }
.rec-card .name      { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.rec-card .score-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; }
.rec-card .score-num { font-size: 1.4rem; font-weight: 800; color: #0f172a; }
.rec-card .score-bar-bg { flex: 1; height: 6px; background: #e2e8f0; border-radius: 3px; }
.rec-card.primary .score-bar-fill { height: 6px; background: #22c55e; border-radius: 3px; }
.rec-card.backup  .score-bar-fill { height: 6px; background: #3b82f6; border-radius: 3px; }
.rec-card .reasoning { font-size: 0.86rem; color: #475569; line-height: 1.6; }

/* ── Alert cards ── */
.alert-card {
    border-radius: 10px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem; border-left: 5px solid;
}
.alert-card.high   { background: #fff1f2; border-color: #f43f5e; }
.alert-card.medium { background: #fffbeb; border-color: #f59e0b; }
.alert-card.low    { background: #eff6ff; border-color: #3b82f6; }
.alert-card .ah { font-weight: 700; font-size: 0.88rem; margin-bottom: 0.3rem; }
.alert-card.high   .ah { color: #be123c; }
.alert-card.medium .ah { color: #b45309; }
.alert-card.low    .ah { color: #1d4ed8; }
.alert-card .ab { font-size: 0.83rem; color: #475569; line-height: 1.5; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin-bottom: 1rem; }
.metric-card {
    flex: 1; background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1rem; text-align: center;
}
.metric-card .ml { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
.metric-card .mv { font-size: 1.8rem; font-weight: 800; }
.metric-card.high-card   .mv { color: #f43f5e; }
.metric-card.medium-card .mv { color: #f59e0b; }
.metric-card.low-card    .mv { color: #3b82f6; }

/* ── Insight & action boxes ── */
.insight-box {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 1.1rem 1.3rem; font-size: 0.9rem;
    color: #1e3a5f; line-height: 1.7; margin-bottom: 1rem;
}
.action-box {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 1px solid #fde68a; border-radius: 10px;
    padding: 1.1rem 1.3rem; font-size: 0.9rem;
    color: #78350f; line-height: 1.7;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
.sidebar-section {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 0.8rem;
}
.sidebar-label {
    font-size: 0.72rem; font-weight: 700;
    color: #64748b; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 0.5rem;
}

/* ── Landing cards ── */
.landing-card {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; height: 100%;
}
.landing-card .lc-icon { font-size: 2rem; margin-bottom: 0.7rem; }
.landing-card .lc-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem; }
.landing-card .lc-body  { font-size: 0.83rem; color: #64748b; line-height: 1.6; }

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NAVBAR WITH LOGOS
# ─────────────────────────────────────────────

st.markdown(f"""
<div class="navbar">
    <div class="navbar-left">
        <img src="{gcx_b64}" class="navbar-logo" alt="GCX"/>
        <div class="navbar-divider"></div>
        <img src="{prodapt_b64}" class="navbar-logo" alt="Prodapt"/>
        <div class="navbar-divider"></div>
        <span class="navbar-title">Carrier & Supplier Intelligence Engine</span>
    </div>
    <div class="navbar-right">
        <span class="navbar-badge">📡 Telecom</span>
        <span class="navbar-badge">🤖 AI Powered</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-tag">AI-Driven Performance Intelligence</div>
    <h1>Smart Partner Selection<br>for <span>Telecom Delivery</span></h1>
    <p>
        Analyse historical carrier and supplier performance to recommend
        the most reliable and cost-effective partner combination for any
        service request — backed by AI scoring and risk intelligence.
    </p>
    <div class="hero-stats">
        <div>
            <div class="hero-stat-value">15</div>
            <div class="hero-stat-label">Carriers</div>
        </div>
        <div>
            <div class="hero-stat-value">12</div>
            <div class="hero-stat-label">Suppliers</div>
        </div>
        <div>
            <div class="hero-stat-value">7</div>
            <div class="hero-stat-label">Countries</div>
        </div>
        <div>
            <div class="hero-stat-value">9</div>
            <div class="hero-stat-label">Service Types</div>
        </div>
        <div>
            <div class="hero-stat-value">12mo</div>
            <div class="hero-stat-label">Data Window</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🎯 Service Requirement")
    st.markdown("---")

    country      = st.selectbox("🌍 Country",      get_countries())
    service_type = st.selectbox("🔧 Service Type", get_service_types())

    st.markdown("#### 📅 Expected Delivery")
    quick_options = {
        "15 days"     : 15,
        "30 days"     : 30,
        "60 days"     : 60,
        "90 days"     : 90,
        "Custom date" : None,
    }
    quick_select = st.selectbox("Quick Select", list(quick_options.keys()))

    if quick_select == "Custom date":
        min_date      = datetime.date.today() + datetime.timedelta(days=1)
        custom_date   = st.date_input("Pick a date", min_value=min_date, value=min_date)
        expected_days = (custom_date - datetime.date.today()).days
        st.caption(f"That is **{expected_days} days** from today.")
    else:
        expected_days = quick_options[quick_select]

    st.markdown("")
    run_button = st.button("🔍 Analyse Partners", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("#### ℹ️ How it works")
    st.markdown("**1.** Select country, service & deadline")
    st.markdown("**2.** Click Analyse Partners")
    st.markdown("**3.** AI scores all eligible partners")
    st.markdown("**4.** Review scores, trends & alerts")

    # PDF download
    if "pdf_result" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📄 Export")
        pdf_bytes = generate_pdf(
            st.session_state["pdf_country"],
            st.session_state["pdf_service"],
            st.session_state["pdf_result"],
            st.session_state["pdf_alerts"],
        )
        st.download_button(
            label               = "⬇️ Download PDF Report",
            data                = pdf_bytes,
            file_name           = f"report_{st.session_state['pdf_country']}_{st.session_state['pdf_service'].replace('/', '_')}.pdf",
            mime                = "application/pdf",
            use_container_width = True,
        )


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def render_rec_card(card_type, partner_type, data):
    icon   = "✅" if card_type == "primary" else "🔄"
    tag    = f"{icon} {'Primary' if card_type == 'primary' else 'Backup'} {partner_type}"
    name   = data.get("carrier_name") or data.get("supplier_name", "")
    score  = data.get("score", 0)
    reason = data.get("reasoning", "")
    width  = max(0, min(100, score))
    st.markdown(f"""
    <div class="rec-card {card_type}">
        <div class="tag">{tag}</div>
        <div class="name">{name}</div>
        <div class="score-row">
            <span class="score-num">{score}</span>
            <span style="font-size:0.8rem;color:#94a3b8;">/100</span>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{width}%"></div>
            </div>
        </div>
        <div class="reasoning">{reason}</div>
    </div>
    """, unsafe_allow_html=True)


def render_alert_card(alert):
    sev   = alert["severity"].lower()
    icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    icon  = icons.get(sev, "⚪")
    st.markdown(f"""
    <div class="alert-card {sev}">
        <div class="ah">{icon} {alert['severity']} · {alert['partner_type']}: {alert['partner_name']} ({alert['partner_id']})</div>
        <div class="ab"><strong>Issue:</strong> {alert['issue']} &nbsp;|&nbsp; <strong>Actual:</strong> {alert['actual_value']} &nbsp;|&nbsp; <strong>Threshold:</strong> {alert['threshold']}</div>
    </div>
    """, unsafe_allow_html=True)


def colour_sla(val):
    return "background-color: #bbf7d0; color: #14532d" if val >= 80 else "background-color: #fecdd3; color: #881337"

def colour_delay(val):
    return "background-color: #bbf7d0; color: #14532d" if val <= 20 else "background-color: #fecdd3; color: #881337"

def colour_quality(val):
    return "background-color: #bbf7d0; color: #14532d" if val >= 75 else "background-color: #fecdd3; color: #881337"

def colour_fulfillment(val):
    return "background-color: #bbf7d0; color: #14532d" if val >= 80 else "background-color: #fecdd3; color: #881337"

def colour_cost(val):
    if val <= 1.1:   return "background-color: #bbf7d0; color: #14532d"
    elif val <= 1.3: return "background-color: #fef08a; color: #713f12"
    else:            return "background-color: #fecdd3; color: #881337"


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

if run_button:

    # Results bar
    st.markdown(f"""
    <div class="results-bar">
        <span class="results-bar-title">📊 Analysis Results</span>
        <span class="pill pill-blue">🌍 {country}</span>
        <span class="pill pill-blue">🔧 {service_type}</span>
        <span class="pill pill-orange">📅 {expected_days} days expected</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 AI Recommendation",
        "📊 Partner Scorecards",
        "🚨 Risk Alerts",
        "📈 Trends",
        "🔍 Raw Data",
    ])


    # ── TAB 1 ───────────────────────────────────
    with tab1:
        with st.spinner("Analysing partner performance..."):
            result = get_recommendation(country, service_type, expected_days)

        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state["pdf_result"]  = result
            st.session_state["pdf_alerts"]  = get_all_alerts(country, service_type)
            st.session_state["pdf_country"] = country
            st.session_state["pdf_service"] = service_type

            st.markdown('<div class="section-title">📶 Carrier Recommendation</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: render_rec_card("primary", "Carrier",  result["primary_carrier"])
            with col2: render_rec_card("backup",  "Carrier",  result["backup_carrier"])

            st.markdown('<div class="section-title">📦 Supplier Recommendation</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3: render_rec_card("primary", "Supplier", result["primary_supplier"])
            with col4: render_rec_card("backup",  "Supplier", result["backup_supplier"])

            st.markdown('<div class="section-title">📈 Trend Insight</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-box">{result["trend_insight"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">📋 Action Plan</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="action-box">{result["action_plan"]}</div>', unsafe_allow_html=True)


    # ── TAB 2 ───────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">📶 Carrier Scorecards</div>', unsafe_allow_html=True)
        carriers_df = filter_carriers(country, service_type)

        if carriers_df.empty:
            st.warning("No carriers found for this selection.")
        else:
            display = carriers_df.rename(columns={
                "carrier_id"          : "ID",
                "carrier_name"        : "Carrier",
                "country"             : "Country",
                "service_type"        : "Service",
                "avg_sla_adherence"   : "SLA % (avg)",
                "avg_lead_time_days"  : "Lead Time (days)",
                "avg_delay_rate"      : "Delay Rate %",
                "total_jobs"          : "Jobs (3mo)",
                "total_penalty_events": "Penalties",
            })
            styled = display.style\
                .map(colour_sla,   subset=["SLA % (avg)"])\
                .map(colour_delay, subset=["Delay Rate %"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown('<div class="section-title">📦 Supplier Scorecards</div>', unsafe_allow_html=True)
        suppliers_df = filter_suppliers(service_type)

        if suppliers_df.empty:
            st.warning("No suppliers found for this selection.")
        else:
            display = suppliers_df.rename(columns={
                "supplier_id"         : "ID",
                "supplier_name"       : "Supplier",
                "service_type"        : "Service",
                "avg_cost_index"      : "Cost Index",
                "avg_quality_score"   : "Quality Score",
                "avg_fulfillment_rate": "Fulfillment %",
                "avg_billing_accuracy": "Billing Accuracy %",
                "total_disputes"      : "Disputes (3mo)",
                "total_orders"        : "Orders (3mo)",
            })
            styled = display.style\
                .map(colour_quality,     subset=["Quality Score"])\
                .map(colour_fulfillment, subset=["Fulfillment %"])\
                .map(colour_cost,        subset=["Cost Index"])
            st.dataframe(styled, use_container_width=True, hide_index=True)


    # ── TAB 3 ───────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">🚨 Risk Alerts</div>', unsafe_allow_html=True)
        alerts = get_all_alerts(country, service_type)

        if not alerts:
            st.success("✅ No alerts — all partners within acceptable thresholds.")
        else:
            high_c   = sum(1 for a in alerts if a["severity"] == "High")
            medium_c = sum(1 for a in alerts if a["severity"] == "Medium")
            low_c    = sum(1 for a in alerts if a["severity"] == "Low")

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card high-card"><div class="ml">🔴 High</div><div class="mv">{high_c}</div></div>',     unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card medium-card"><div class="ml">🟡 Medium</div><div class="mv">{medium_c}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card low-card"><div class="ml">🟢 Low</div><div class="mv">{low_c}</div></div>',           unsafe_allow_html=True)

            st.markdown("")
            for alert in alerts:
                render_alert_card(alert)


    # ── TAB 4 ───────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">📈 Performance Trends — Last 12 Months</div>', unsafe_allow_html=True)
        st.caption("Each line = one partner. Hover to see exact values.")

        carrier_trends  = get_carrier_trends(country, service_type)
        supplier_trends = get_supplier_trends(service_type)

        st.markdown("#### 📶 Carrier Trends")
        if carrier_trends.empty:
            st.warning("No carrier trend data for this selection.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**SLA Adherence % — higher is better**")
                st.line_chart(carrier_trends.pivot_table(index="month", columns="carrier_name", values="sla_adherence_pct"), use_container_width=True)
            with col2:
                st.markdown("**Delay Rate % — lower is better**")
                st.line_chart(carrier_trends.pivot_table(index="month", columns="carrier_name", values="install_delay_rate_pct"), use_container_width=True)
            st.markdown("**Lead Time (days) — lower is better**")
            st.line_chart(carrier_trends.pivot_table(index="month", columns="carrier_name", values="actual_lead_time_days"), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📦 Supplier Trends")
        if supplier_trends.empty:
            st.warning("No supplier trend data for this selection.")
        else:
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Quality Score — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="quality_score"), use_container_width=True)
            with col4:
                st.markdown("**Fulfillment Rate % — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="fulfillment_rate_pct"), use_container_width=True)
            col5, col6 = st.columns(2)
            with col5:
                st.markdown("**Billing Accuracy % — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="billing_accuracy_pct"), use_container_width=True)
            with col6:
                st.markdown("**Cost Index — lower is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="cost_index"), use_container_width=True)


    # ── TAB 5 ───────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">📂 Raw Carrier Data — Last 3 Months</div>', unsafe_allow_html=True)
        st.dataframe(filter_carriers(country, service_type), use_container_width=True, hide_index=True)
        st.markdown("---")
        st.markdown('<div class="section-title">📂 Raw Supplier Data — Last 3 Months</div>', unsafe_allow_html=True)
        st.dataframe(filter_suppliers(service_type), use_container_width=True, hide_index=True)


# ── LANDING ──────────────────────────────────
else:
    st.info("💡 Tip: Use the **>** arrow on the top left to open the sidebar if it's hidden.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="landing-card">
            <div class="lc-icon">🌍</div>
            <div class="lc-title">Step 1 — Select Requirement</div>
            <div class="lc-body">Choose the country, service type and customer expected delivery deadline from the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="landing-card">
            <div class="lc-icon">🤖</div>
            <div class="lc-title">Step 2 — Run AI Analysis</div>
            <div class="lc-body">Click Analyse Partners. The AI engine scores all eligible carriers and suppliers using historical KPIs.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="landing-card">
            <div class="lc-icon">📊</div>
            <div class="lc-title">Step 3 — Review & Export</div>
            <div class="lc-body">Review AI recommendations, risk alerts, trend charts and download a PDF report for your client.</div>
        </div>
        """, unsafe_allow_html=True)