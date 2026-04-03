# utils/pdf_export.py
# Generates a downloadable PDF report of the AI recommendation

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────

DARK_BLUE  = colors.HexColor("#2c5364")
MID_BLUE   = colors.HexColor("#203a43")
LIGHT_BLUE = colors.HexColor("#ebf8ff")
GREEN      = colors.HexColor("#38a169")
LIGHT_GREEN= colors.HexColor("#f0fff4")
AMBER      = colors.HexColor("#d69e2e")
RED        = colors.HexColor("#e53e3e")
LIGHT_GREY = colors.HexColor("#f8f9fa")
MID_GREY   = colors.HexColor("#e0e0e0")
TEXT_DARK  = colors.HexColor("#1a1a2e")
TEXT_MID   = colors.HexColor("#444444")


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title",
            fontSize    = 20,
            fontName    = "Helvetica-Bold",
            textColor   = colors.white,
            alignment   = TA_LEFT,
            spaceAfter  = 4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontSize    = 10,
            fontName    = "Helvetica",
            textColor   = colors.HexColor("#a0c4d8"),
            alignment   = TA_LEFT,
            spaceAfter  = 0,
        ),
        "section": ParagraphStyle(
            "section",
            fontSize    = 12,
            fontName    = "Helvetica-Bold",
            textColor   = DARK_BLUE,
            spaceBefore = 14,
            spaceAfter  = 6,
        ),
        "card_tag": ParagraphStyle(
            "card_tag",
            fontSize    = 8,
            fontName    = "Helvetica-Bold",
            textColor   = GREEN,
            spaceAfter  = 2,
        ),
        "card_tag_backup": ParagraphStyle(
            "card_tag_backup",
            fontSize    = 8,
            fontName    = "Helvetica-Bold",
            textColor   = DARK_BLUE,
            spaceAfter  = 2,
        ),
        "card_name": ParagraphStyle(
            "card_name",
            fontSize    = 13,
            fontName    = "Helvetica-Bold",
            textColor   = TEXT_DARK,
            spaceAfter  = 2,
        ),
        "card_score": ParagraphStyle(
            "card_score",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = TEXT_MID,
            spaceAfter  = 4,
        ),
        "card_body": ParagraphStyle(
            "card_body",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = TEXT_DARK,
            leading     = 14,
            spaceAfter  = 0,
        ),
        "body": ParagraphStyle(
            "body",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = TEXT_DARK,
            leading     = 14,
            spaceAfter  = 6,
        ),
        "alert_high": ParagraphStyle(
            "alert_high",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = colors.HexColor("#c53030"),
            leading     = 14,
            spaceAfter  = 3,
        ),
        "alert_medium": ParagraphStyle(
            "alert_medium",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = colors.HexColor("#b7791f"),
            leading     = 14,
            spaceAfter  = 3,
        ),
        "alert_low": ParagraphStyle(
            "alert_low",
            fontSize    = 9,
            fontName    = "Helvetica",
            textColor   = colors.HexColor("#2b6cb0"),
            leading     = 14,
            spaceAfter  = 3,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontSize    = 8,
            fontName    = "Helvetica",
            textColor   = colors.HexColor("#999999"),
            alignment   = TA_CENTER,
        ),
    }
    return styles


# ─────────────────────────────────────────────
# HELPER — two column table for rec cards
# ─────────────────────────────────────────────

def rec_card_table(primary_content, backup_content):
    """
    Places primary and backup recommendation side by side
    using a two-column table.
    """
    data = [[primary_content, backup_content]]
    table = Table(data, colWidths=[8.5*cm, 8.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, 0), LIGHT_GREEN),
        ("BACKGROUND",  (1, 0), (1, 0), LIGHT_BLUE),
        ("BOX",         (0, 0), (0, 0), 0.5, GREEN),
        ("BOX",         (1, 0), (1, 0), 0.5, DARK_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0,0), (-1, -1), 10),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]))
    return table


# ─────────────────────────────────────────────
# MAIN FUNCTION — generate PDF bytes
# ─────────────────────────────────────────────

def generate_pdf(region, service_type, result, alerts):
    """
    Generates a PDF report and returns it as bytes.
    'result' is the JSON dict returned by get_recommendation()
    'alerts' is the list returned by get_all_alerts()
    """

    # We write to memory (not a file on disk)
    buffer = io.BytesIO()
    styles = build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize     = A4,
        leftMargin   = 2*cm,
        rightMargin  = 2*cm,
        topMargin    = 2*cm,
        bottomMargin = 2*cm,
    )

    elements = []
    W = 17*cm   # usable page width


    # ── HEADER BANNER ────────────────────────
    header_data = [[
        Paragraph("📡 Carrier & Supplier Performance Intelligence Engine", styles["title"]),
        Paragraph("AI-Driven Telecom Partner Selection · Powered by LLaMA 3.3 via Groq", styles["subtitle"]),
    ]]
    header_table = Table(header_data, colWidths=[W])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), DARK_BLUE),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6]),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.4*cm))


    # ── REQUEST DETAILS TABLE ────────────────
    elements.append(Paragraph("Service Request Details", styles["section"]))

    req_data = [
        ["Region",       region],
        ["Service Type", service_type],
        ["Data Window",  "Last 3 months of historical performance"],
        ["AI Model",     "LLaMA 3.3 70B via Groq"],
    ]
    req_table = Table(req_data, colWidths=[4*cm, 13*cm])
    req_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, -1), LIGHT_GREY),
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",    (0, 0), (-1, -1), TEXT_DARK),
        ("GRID",         (0, 0), (-1, -1), 0.4, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    elements.append(req_table)
    elements.append(Spacer(1, 0.3*cm))


    # ── CARRIER RECOMMENDATION ───────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Paragraph("Carrier Recommendation", styles["section"]))

    pc = result["primary_carrier"]
    bc = result["backup_carrier"]

    primary_content = [
        Paragraph("✅  PRIMARY CARRIER", styles["card_tag"]),
        Paragraph(pc["carrier_name"],    styles["card_name"]),
        Paragraph(f"Score: {pc['score']} / 100", styles["card_score"]),
        Paragraph(pc["reasoning"],       styles["card_body"]),
    ]
    backup_content = [
        Paragraph("🔄  BACKUP CARRIER",  styles["card_tag_backup"]),
        Paragraph(bc["carrier_name"],    styles["card_name"]),
        Paragraph(f"Score: {bc['score']} / 100", styles["card_score"]),
        Paragraph(bc["reasoning"],       styles["card_body"]),
    ]
    elements.append(rec_card_table(primary_content, backup_content))
    elements.append(Spacer(1, 0.3*cm))


    # ── SUPPLIER RECOMMENDATION ───────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Paragraph("Supplier Recommendation", styles["section"]))

    ps = result["primary_supplier"]
    bs = result["backup_supplier"]

    primary_content = [
        Paragraph("✅  PRIMARY SUPPLIER", styles["card_tag"]),
        Paragraph(ps["supplier_name"],   styles["card_name"]),
        Paragraph(f"Score: {ps['score']} / 100", styles["card_score"]),
        Paragraph(ps["reasoning"],       styles["card_body"]),
    ]
    backup_content = [
        Paragraph("🔄  BACKUP SUPPLIER", styles["card_tag_backup"]),
        Paragraph(bs["supplier_name"],   styles["card_name"]),
        Paragraph(f"Score: {bs['score']} / 100", styles["card_score"]),
        Paragraph(bs["reasoning"],       styles["card_body"]),
    ]
    elements.append(rec_card_table(primary_content, backup_content))
    elements.append(Spacer(1, 0.3*cm))


    # ── RISK ALERTS ───────────────────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Paragraph("Risk Alerts", styles["section"]))

    if not alerts:
        elements.append(Paragraph("✅ No alerts — all partners within acceptable thresholds.", styles["body"]))
    else:
        high_count   = sum(1 for a in alerts if a["severity"] == "High")
        medium_count = sum(1 for a in alerts if a["severity"] == "Medium")
        low_count    = sum(1 for a in alerts if a["severity"] == "Low")

        summary_data = [
            ["🔴 High", "🟡 Medium", "🟢 Low"],
            [str(high_count), str(medium_count), str(low_count)],
        ]
        summary_table = Table(summary_data, colWidths=[W/3, W/3, W/3])
        summary_table.setStyle(TableStyle([
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 10),
            ("FONTSIZE",     (0, 1), (-1, 1), 18),
            ("TEXTCOLOR",    (0, 0), (0, -1), RED),
            ("TEXTCOLOR",    (1, 0), (1, -1), AMBER),
            ("TEXTCOLOR",    (2, 0), (2, -1), DARK_BLUE),
            ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND",   (0, 0), (-1, -1), LIGHT_GREY),
            ("GRID",         (0, 0), (-1, -1), 0.4, MID_GREY),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*cm))

        # Individual alerts
        for a in alerts:
            sev    = a["severity"]
            style  = styles[f"alert_{sev.lower()}"]
            icons  = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            icon   = icons.get(sev, "•")
            text   = (
                f"<b>{icon} {sev}</b> · {a['partner_type']}: <b>{a['partner_name']}</b> "
                f"({a['partner_id']}) — {a['issue']} "
                f"[Actual: {a['actual_value']} | Threshold: {a['threshold']}]"
            )
            elements.append(Paragraph(text, style))


    # ── TREND INSIGHT ─────────────────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Paragraph("Trend Insight", styles["section"]))
    elements.append(Paragraph(result.get("trend_insight", ""), styles["body"]))


    # ── ACTION PLAN ───────────────────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Paragraph("Action Plan", styles["section"]))

    action_data = [[Paragraph(result.get("action_plan", ""), styles["body"])]]
    action_table = Table(action_data, colWidths=[W])
    action_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
        ("BOX",          (0, 0), (-1, -1), 0.5, AMBER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    elements.append(action_table)
    elements.append(Spacer(1, 0.5*cm))


    # ── FOOTER ───────────────────────────────
    elements.append(HRFlowable(width=W, thickness=0.5, color=MID_GREY))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Generated by AI-Driven Carrier &amp; Supplier Performance Intelligence Engine · Confidential",
        styles["footer"]
    ))

    # Build PDF into buffer
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()