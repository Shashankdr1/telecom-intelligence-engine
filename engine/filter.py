# engine/filter.py

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_carriers, load_suppliers

LOOKBACK_MONTHS = 3


def get_recent_months(df, n=LOOKBACK_MONTHS):
    recent = sorted(df["month"].unique())[-n:]
    return df[df["month"].isin(recent)]


def filter_carriers(country: str, service_type: str) -> pd.DataFrame:
    df = load_carriers()

    filtered = df[
        (df["country"] == country) &
        (df["service_type"] == service_type)
    ]

    filtered = get_recent_months(filtered)

    if filtered.empty:
        return pd.DataFrame()

    summary = filtered.groupby(["carrier_id", "carrier_name", "country", "service_type"]).agg(
        avg_sla_adherence     = ("sla_adherence_pct",      "mean"),
        avg_lead_time_days    = ("actual_lead_time_days",  "mean"),
        avg_delay_rate        = ("install_delay_rate_pct", "mean"),
        total_jobs            = ("jobs_completed",         "sum"),
        total_penalty_events  = ("sla_penalty_events",     "sum"),
    ).reset_index()

    return summary.round(1)


def filter_suppliers(service_type: str) -> pd.DataFrame:
    df = load_suppliers()

    filtered = df[df["service_type"] == service_type]
    filtered = get_recent_months(filtered)

    if filtered.empty:
        return pd.DataFrame()

    summary = filtered.groupby(["supplier_id", "supplier_name", "service_type"]).agg(
        avg_cost_index        = ("cost_index",           "mean"),
        avg_quality_score     = ("quality_score",        "mean"),
        avg_fulfillment_rate  = ("fulfillment_rate_pct", "mean"),
        avg_billing_accuracy  = ("billing_accuracy_pct", "mean"),
        total_disputes        = ("dispute_count",        "sum"),
        total_orders          = ("orders_handled",       "sum"),
    ).reset_index()

    return summary.round(1)


def get_carrier_trends(country: str, service_type: str) -> pd.DataFrame:
    df = load_carriers()

    filtered = df[
        (df["country"] == country) &
        (df["service_type"] == service_type)
    ]

    if filtered.empty:
        return pd.DataFrame()

    trend = filtered[[
        "month",
        "carrier_name",
        "sla_adherence_pct",
        "install_delay_rate_pct",
        "actual_lead_time_days"
    ]].copy()

    return trend.sort_values("month")


def get_supplier_trends(service_type: str) -> pd.DataFrame:
    df = load_suppliers()

    filtered = df[df["service_type"] == service_type]

    if filtered.empty:
        return pd.DataFrame()

    trend = filtered[[
        "month",
        "supplier_name",
        "quality_score",
        "fulfillment_rate_pct",
        "billing_accuracy_pct",
        "cost_index"
    ]].copy()

    return trend.sort_values("month")


if __name__ == "__main__":
    print("Testing filter.py...\n")

    country      = "India"
    service_type = "Fiber Broadband"

    print(f"Requirement: {service_type} in {country}\n")

    carriers = filter_carriers(country, service_type)
    print(f"Eligible Carriers ({len(carriers)} found):")
    print(carriers.to_string(index=False))

    print()

    suppliers = filter_suppliers(service_type)
    print(f"Eligible Suppliers ({len(suppliers)} found):")
    print(suppliers.to_string(index=False))