# app.py
import streamlit as st
import pandas as pd
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers   import get_countries, get_service_types
from engine.filter   import filter_carriers, filter_suppliers, get_carrier_trends, get_supplier_trends
from engine.scorer   import get_recommendation
from engine.alerts   import get_all_alerts
from utils.pdf_export import generate_pdf


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title = "Telecom Performance Intelligence Engine",
    page_icon  = "📡",
    layout     = "wide"
)


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
.banner {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.banner h1 { color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0 0 0.3rem 0; }
.banner p  { color: #a0c4d8; font-size: 0.95rem; margin: 0; }

.section-title {
    font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
    border-left: 4px solid #2c5364;
    padding-left: 0.6rem; margin: 1.2rem 0 0.8rem 0;
}

.metric-card { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 10px; padding: 1rem 1.2rem; text-align: center; }
.metric-card .label { font-size: 0.78rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
.metric-card .value { font-size: 1.6rem; font-weight: 700; color: #2c5364; }

.req-pill {
    display: inline-block; background: #e8f4fd; color: #1a5276;
    border: 1px solid #aed6f1; border-radius: 20px;
    padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;
    margin: 0.2rem 0.2rem 0.8rem 0;
}

.rec-card { border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; border: 1px solid #e0e0e0; }
.rec-card.primary { background: #f0fff4; border-left: 5px solid #38a169; }
.rec-card.backup  { background: #ebf8ff; border-left: 5px solid #3182ce; }
.rec-card .tag    { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.rec-card.primary .tag { color: #38a169; }
.rec-card.backup  .tag { color: #3182ce; }
.rec-card .name      { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.3rem; }
.rec-card .score     { font-size: 0.85rem; color: #555; margin-bottom: 0.5rem; }
.rec-card .reasoning { font-size: 0.88rem; color: #333; line-height: 1.5; }

.alert-card { border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; border-left: 5px solid; }
.alert-card.high   { background: #fff5f5; border-color: #e53e3e; }
.alert-card.medium { background: #fffbeb; border-color: #d69e2e; }
.alert-card.low    { background: #ebf8ff; border-color: #3182ce; }
.alert-card .alert-header { font-weight: 700; font-size: 0.88rem; margin-bottom: 0.3rem; }
.alert-card.high   .alert-header { color: #c53030; }
.alert-card.medium .alert-header { color: #b7791f; }
.alert-card.low    .alert-header { color: #2b6cb0; }
.alert-card .alert-body { font-size: 0.84rem; color: #444; line-height: 1.5; }

.insight-box { background: #f0f7ff; border: 1px solid #bee3f8; border-radius: 8px; padding: 1rem 1.2rem; font-size: 0.9rem; color: #2a4365; line-height: 1.6; margin-bottom: 1rem; }
.action-box  { background: #fffbeb; border: 1px solid #fbd38d; border-radius: 8px; padding: 1rem 1.2rem; font-size: 0.9rem; color: #744210; line-height: 1.6; }

[data-testid="stSidebar"] { background: #f4f6f9; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────

st.markdown("""
<div class="banner">
    <h1>📡 Carrier & Supplier Performance Intelligence Engine</h1>
    <p>AI-Driven Telecom Partner Selection · Powered by LLaMA 3.3 70B via Groq</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — INPUTS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 Service Requirement")
    st.markdown("Fill in the details of the incoming request.")
    st.markdown("---")

    # Country
    country      = st.selectbox("🌍 Country",      get_countries())

    # Service type
    service_type = st.selectbox("🔧 Service Type", get_service_types())

    st.markdown("#### 📅 Customer Expected Delivery")

    # Quick select dropdown
    quick_options = {
        "15 days"  : 15,
        "30 days"  : 30,
        "60 days"  : 60,
        "90 days"  : 90,
        "Custom date" : None,
    }
    quick_select = st.selectbox("Quick Select", list(quick_options.keys()))

    # If custom — show date picker
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
    st.markdown("#### How it works")
    st.markdown("**1.** Select country, service & deadline")
    st.markdown("**2.** Click Analyse Partners")
    st.markdown("**3.** AI scores all eligible partners")
    st.markdown("**4.** Review recommendations & alerts")
    st.markdown("---")
    st.caption("Sample data: Jan–Dec 2024 · 15 carriers · 12 suppliers · 7 countries")

    # PDF download — appears after analysis
    if "pdf_result" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📄 Download Report")
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
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def render_rec_card(card_type, partner_type, data):
    icon   = "✅" if card_type == "primary" else "🔄"
    tag    = f"{'Primary' if card_type == 'primary' else 'Backup'} {partner_type}"
    name   = data.get("carrier_name") or data.get("supplier_name", "")
    score  = data.get("score", 0)
    reason = data.get("reasoning", "")
    st.markdown(f"""
    <div class="rec-card {card_type}">
        <div class="tag">{icon} {tag}</div>
        <div class="name">{name}</div>
        <div class="score">Score: <strong>{score} / 100</strong></div>
        <div class="reasoning">{reason}</div>
    </div>
    """, unsafe_allow_html=True)


def render_alert_card(alert):
    sev   = alert["severity"].lower()
    icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    icon  = icons.get(sev, "⚪")
    st.markdown(f"""
    <div class="alert-card {sev}">
        <div class="alert-header">
            {icon} {alert['severity']} · {alert['partner_type']}: {alert['partner_name']} ({alert['partner_id']})
        </div>
        <div class="alert-body">
            <strong>Issue:</strong> {alert['issue']}<br>
            <strong>Actual:</strong> {alert['actual_value']} &nbsp;|&nbsp; <strong>Threshold:</strong> {alert['threshold']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def colour_sla(val):
    return "background-color: #c6efce" if val >= 80 else "background-color: #ffc7ce"

def colour_delay(val):
    return "background-color: #c6efce" if val <= 20 else "background-color: #ffc7ce"

def colour_quality(val):
    return "background-color: #c6efce" if val >= 75 else "background-color: #ffc7ce"

def colour_fulfillment(val):
    return "background-color: #c6efce" if val >= 80 else "background-color: #ffc7ce"

def colour_cost(val):
    if val <= 1.1:   return "background-color: #c6efce"
    elif val <= 1.3: return "background-color: #ffeb9c"
    else:            return "background-color: #ffc7ce"


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

if run_button:

    st.markdown(f"### Results · {service_type} in {country} · Delivery within {expected_days} days")

    # Requirement pills
    st.markdown(f"""
    <span class="req-pill">🌍 {country}</span>
    <span class="req-pill">🔧 {service_type}</span>
    <span class="req-pill">📅 {expected_days} days expected</span>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 AI Recommendation",
        "📊 Partner Scorecards",
        "🚨 Risk Alerts",
        "📈 Trends",
        "🔍 Raw Data",
    ])


    # ── TAB 1 — AI RECOMMENDATION ───────────────
    with tab1:
        with st.spinner("Calling Groq AI — analysing partner performance..."):
            result = get_recommendation(country, service_type, expected_days)

        if "error" in result:
            st.error(result["error"])
        else:
            # Save to session state for PDF
            st.session_state["pdf_result"]  = result
            st.session_state["pdf_alerts"]  = get_all_alerts(country, service_type)
            st.session_state["pdf_country"] = country
            st.session_state["pdf_service"] = service_type

            st.markdown('<div class="section-title">📶 Carrier Recommendation</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: render_rec_card("primary", "Carrier",  result["primary_carrier"])
            with col2: render_rec_card("backup",  "Carrier",  result["backup_carrier"])

            st.markdown("")
            st.markdown('<div class="section-title">📦 Supplier Recommendation</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3: render_rec_card("primary", "Supplier", result["primary_supplier"])
            with col4: render_rec_card("backup",  "Supplier", result["backup_supplier"])

            st.markdown("")
            st.markdown('<div class="section-title">📈 Trend Insight</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-box">{result["trend_insight"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">📋 Action Plan</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="action-box">{result["action_plan"]}</div>', unsafe_allow_html=True)


    # ── TAB 2 — PARTNER SCORECARDS ──────────────
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


    # ── TAB 3 — RISK ALERTS ─────────────────────
    with tab3:
        st.markdown('<div class="section-title">🚨 Risk Alerts</div>', unsafe_allow_html=True)
        alerts = get_all_alerts(country, service_type)

        if not alerts:
            st.success("✅ No alerts — all partners are within acceptable thresholds.")
        else:
            high_count   = sum(1 for a in alerts if a["severity"] == "High")
            medium_count = sum(1 for a in alerts if a["severity"] == "Medium")
            low_count    = sum(1 for a in alerts if a["severity"] == "Low")

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><div class="label">🔴 High</div><div class="value">{high_count}</div></div>',   unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><div class="label">🟡 Medium</div><div class="value">{medium_count}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><div class="label">🟢 Low</div><div class="value">{low_count}</div></div>',       unsafe_allow_html=True)

            st.markdown("")
            for alert in alerts:
                render_alert_card(alert)


    # ── TAB 4 — TRENDS ──────────────────────────
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
                st.markdown("**Installation Delay Rate % — lower is better**")
                st.line_chart(carrier_trends.pivot_table(index="month", columns="carrier_name", values="install_delay_rate_pct"), use_container_width=True)

            st.markdown("**Average Lead Time in Days — lower is better**")
            st.line_chart(carrier_trends.pivot_table(index="month", columns="carrier_name", values="actual_lead_time_days"), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📦 Supplier Trends")
        if supplier_trends.empty:
            st.warning("No supplier trend data for this selection.")
        else:
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Quality Score / 100 — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="quality_score"), use_container_width=True)
            with col4:
                st.markdown("**Fulfillment Rate % — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="fulfillment_rate_pct"), use_container_width=True)

            col5, col6 = st.columns(2)
            with col5:
                st.markdown("**Billing Accuracy % — higher is better**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="billing_accuracy_pct"), use_container_width=True)
            with col6:
                st.markdown("**Cost Index — lower is better (1.0 = market rate)**")
                st.line_chart(supplier_trends.pivot_table(index="month", columns="supplier_name", values="cost_index"), use_container_width=True)


    # ── TAB 5 — RAW DATA ────────────────────────
    with tab5:
        st.markdown('<div class="section-title">📂 Raw Carrier Data — Last 3 Months</div>', unsafe_allow_html=True)
        st.dataframe(filter_carriers(country, service_type), use_container_width=True, hide_index=True)
        st.markdown("---")
        st.markdown('<div class="section-title">📂 Raw Supplier Data — Last 3 Months</div>', unsafe_allow_html=True)
        st.dataframe(filter_suppliers(service_type), use_container_width=True, hide_index=True)


# ── LANDING STATE ────────────────────────────
else:
    st.markdown("### 👈 Select your requirement from the sidebar to begin")
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    c1.info("**Step 1**\n\nChoose country, service type & expected delivery")
    c2.info("**Step 2**\n\nClick **Analyse Partners** to run the AI engine")
    c3.info("**Step 3**\n\nReview scores, trends, alerts & download PDF")