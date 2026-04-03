# engine/alerts.py
# This file runs rule-based checks on carrier and supplier data
# Think of it as an automatic "early warning system"
# It flags partners whose numbers cross dangerous thresholds

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.filter import filter_carriers, filter_suppliers


# ─────────────────────────────────────────────
# THRESHOLDS
# These are the "danger lines" — if a partner crosses these,
# we raise an alert. You can tune these later with real data.
# ─────────────────────────────────────────────

CARRIER_THRESHOLDS = {
    "avg_sla_adherence"  : {"min": 80,  "label": "SLA adherence below 80%"},
    "avg_delay_rate"     : {"max": 20,  "label": "Installation delay rate above 20%"},
    "total_penalty_events": {"max": 10, "label": "More than 10 SLA penalty events"},
    "avg_lead_time_days" : {"max": 20,  "label": "Average lead time above 20 days"},
}

SUPPLIER_THRESHOLDS = {
    "avg_quality_score"   : {"min": 75,  "label": "Quality score below 75"},
    "avg_fulfillment_rate": {"min": 80,  "label": "Fulfillment rate below 80%"},
    "avg_billing_accuracy": {"min": 80,  "label": "Billing accuracy below 80%"},
    "avg_cost_index"      : {"max": 1.3, "label": "Cost index above 1.3 (30% above market)"},
    "total_disputes"      : {"max": 10,  "label": "More than 10 billing disputes"},
}


# ─────────────────────────────────────────────
# SEVERITY CALCULATOR
# Based on how far a value is from the threshold,
# we assign Low / Medium / High severity
# ─────────────────────────────────────────────

def get_severity(value, threshold_type, threshold_value):
    """
    threshold_type: 'min' (value should be above this) or 'max' (value should be below this)
    Returns: 'Low', 'Medium', or 'High'
    """
    if threshold_type == "min":
        gap = threshold_value - value          # How far below the minimum are we?
        pct = (gap / threshold_value) * 100
    else:
        gap = value - threshold_value          # How far above the maximum are we?
        pct = (gap / threshold_value) * 100

    if pct <= 10:
        return "Low"
    elif pct <= 25:
        return "Medium"
    else:
        return "High"


# ─────────────────────────────────────────────
# CHECK CARRIERS
# ─────────────────────────────────────────────

def check_carrier_alerts(country: str, service_type: str) -> list:
    """
    Runs threshold checks on all eligible carriers.
    Returns a list of alert dictionaries.
    """
    carriers_df = filter_carriers(country, service_type)

    if carriers_df.empty:
        return []

    alerts = []

    for _, row in carriers_df.iterrows():
        for column, rules in CARRIER_THRESHOLDS.items():
            value = row[column]

            # Check minimum threshold (value must be ABOVE this)
            if "min" in rules and value < rules["min"]:
                severity = get_severity(value, "min", rules["min"])
                alerts.append({
                    "partner_type" : "Carrier",
                    "partner_name" : row["carrier_name"],
                    "partner_id"   : row["carrier_id"],
                    "issue"        : rules["label"],
                    "actual_value" : round(value, 1),
                    "threshold"    : rules["min"],
                    "severity"     : severity,
                })

            # Check maximum threshold (value must be BELOW this)
            if "max" in rules and value > rules["max"]:
                severity = get_severity(value, "max", rules["max"])
                alerts.append({
                    "partner_type" : "Carrier",
                    "partner_name" : row["carrier_name"],
                    "partner_id"   : row["carrier_id"],
                    "issue"        : rules["label"],
                    "actual_value" : round(value, 1),
                    "threshold"    : rules["max"],
                    "severity"     : severity,
                })

    return alerts


# ─────────────────────────────────────────────
# CHECK SUPPLIERS
# ─────────────────────────────────────────────

def check_supplier_alerts(service_type: str) -> list:
    """
    Runs threshold checks on all eligible suppliers.
    Returns a list of alert dictionaries.
    """
    suppliers_df = filter_suppliers(service_type)

    if suppliers_df.empty:
        return []

    alerts = []

    for _, row in suppliers_df.iterrows():
        for column, rules in SUPPLIER_THRESHOLDS.items():
            value = row[column]

            if "min" in rules and value < rules["min"]:
                severity = get_severity(value, "min", rules["min"])
                alerts.append({
                    "partner_type" : "Supplier",
                    "partner_name" : row["supplier_name"],
                    "partner_id"   : row["supplier_id"],
                    "issue"        : rules["label"],
                    "actual_value" : round(value, 1),
                    "threshold"    : rules["min"],
                    "severity"     : severity,
                })

            if "max" in rules and value > rules["max"]:
                severity = get_severity(value, "max", rules["max"])
                alerts.append({
                    "partner_type" : "Supplier",
                    "partner_name" : row["supplier_name"],
                    "partner_id"   : row["supplier_id"],
                    "issue"        : rules["label"],
                    "actual_value" : round(value, 1),
                    "threshold"    : rules["max"],
                    "severity"     : severity,
                })

    return alerts


# ─────────────────────────────────────────────
# COMBINED ALERTS (carriers + suppliers together)
# ─────────────────────────────────────────────

def get_all_alerts(country: str, service_type: str) -> list:
    carrier_alerts  = check_carrier_alerts(country, service_type)
    supplier_alerts = check_supplier_alerts(service_type)
    all_alerts      = carrier_alerts + supplier_alerts

    # Sort by severity: High first, then Medium, then Low
    severity_order  = {"High": 0, "Medium": 1, "Low": 2}
    all_alerts.sort(key=lambda x: severity_order[x["severity"]])

    return all_alerts


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing alerts.py...\n")

    country      = "India"
    service_type = "Fiber Broadband"

    alerts = get_all_alerts(country, service_type)

    if not alerts:
        print("No alerts found — all partners within thresholds.")
    else:
        print(f"{len(alerts)} alert(s) found:\n")
        for a in alerts:
            print(f"  [{a['severity']:6}] {a['partner_type']} | {a['partner_name']}")
            print(f"           Issue    : {a['issue']}")
            print(f"           Actual   : {a['actual_value']}  |  Threshold: {a['threshold']}")
            print()