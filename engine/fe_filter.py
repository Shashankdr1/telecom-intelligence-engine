# engine/fe_filter.py
# Loads, cleans and filters FE data for analysis

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FE_DATA_PATH   = os.path.join(BASE, "data", "fe_data.csv")

LOOKBACK_MONTHS = 3


# ─────────────────────────────────────────────
# LOAD & CLEAN
# ─────────────────────────────────────────────

def load_fe_data() -> pd.DataFrame:
    df = pd.read_csv(FE_DATA_PATH)

    # Standardise key text columns
    df["Supplier"]                        = df["Supplier"].str.strip().str.upper()
    df["FE Name"]                         = df["FE Name"].str.strip().str.title()
    df["Customer location (Country)"]     = df["Customer location (Country)"].str.strip()
    df["CLOSURE STATUS"]                  = df["CLOSURE STATUS"].str.strip().str.upper()
    df["Closer Measurement"]              = df["Closer Measurement"].str.strip().str.upper()
    df["Task Acceptance"]                 = df["Task Acceptance"].str.strip().str.upper()
    df["FE closure"]                      = df["FE closure"].str.strip().str.upper()

    # Parse month
    df["month_dt"] = pd.to_datetime(df["month"], format="%b-%Y", errors="coerce")

    return df


def get_recent_months(df: pd.DataFrame, n: int = LOOKBACK_MONTHS) -> pd.DataFrame:
    recent = sorted(df["month_dt"].dropna().unique())[-n:]
    return df[df["month_dt"].isin(recent)]


# ─────────────────────────────────────────────
# VENDOR SCORECARD
# Aggregates performance per vendor (SGS / Neeco / NSC)
# ─────────────────────────────────────────────

def get_vendor_scorecard(country: str = None) -> pd.DataFrame:
    df = load_fe_data()

    if country and country != "All":
        df = df[df["Customer location (Country)"] == country]

    df = get_recent_months(df)

    if df.empty:
        return pd.DataFrame()

    # Helper: % of MET in a column
    def met_pct(series):
        return round((series.str.upper() == "MET").sum() / len(series) * 100, 1)

    rows = []
    for vendor, grp in df.groupby("Supplier"):
        closed      = grp[grp["CLOSURE STATUS"] == "TASK CLOSE"]
        total       = len(grp)
        close_rate  = round(len(closed) / total * 100, 1) if total else 0

        rows.append({
            "vendor"              : vendor,
            "total_jobs"          : total,
            "closed_jobs"         : len(closed),
            "closure_rate_pct"    : close_rate,
            "task_acceptance_pct" : met_pct(grp["Task Acceptance"]),
            "fe_closure_pct"      : met_pct(grp["FE closure"]),
            "closer_measurement_pct": met_pct(grp["Closer Measurement"]),
            "avg_duration_hrs"    : round(grp["Duration Hour"].mean(), 1),
            "avg_additional_hrs"  : round(grp["Additional hrs"].mean(), 1),
            "avg_cost_usd"        : round(grp["Converted to USD"].mean(), 1),
            "avg_cost_optimization": round(grp["Cost optimization"].mean(), 1),
            "total_saving_usd"    : round(grp["Basic saving"].sum(), 1),
        })

    return pd.DataFrame(rows).sort_values("closure_rate_pct", ascending=False)


# ─────────────────────────────────────────────
# FE INDIVIDUAL SCORECARD
# Best performing individual FEs
# ─────────────────────────────────────────────

def get_fe_scorecard(country: str = None, vendor: str = None) -> pd.DataFrame:
    df = load_fe_data()

    if country and country != "All":
        df = df[df["Customer location (Country)"] == country]

    if vendor and vendor != "All":
        df = df[df["Supplier"] == vendor.upper()]

    df = get_recent_months(df)

    if df.empty:
        return pd.DataFrame()

    def met_pct(series):
        return round((series.str.upper() == "MET").sum() / len(series) * 100, 1)

    rows = []
    for (fe_name, vendor_name), grp in df.groupby(["FE Name", "Supplier"]):
        if len(grp) < 2:
            continue
        closed     = grp[grp["CLOSURE STATUS"] == "TASK CLOSE"]
        total      = len(grp)
        close_rate = round(len(closed) / total * 100, 1)

        rows.append({
            "fe_name"             : fe_name,
            "vendor"              : vendor_name,
            "total_jobs"          : total,
            "closure_rate_pct"    : close_rate,
            "task_acceptance_pct" : met_pct(grp["Task Acceptance"]),
            "fe_closure_pct"      : met_pct(grp["FE closure"]),
            "avg_duration_hrs"    : round(grp["Duration Hour"].mean(), 1),
            "avg_cost_usd"        : round(grp["Converted to USD"].mean(), 1),
        })

    return pd.DataFrame(rows).sort_values("closure_rate_pct", ascending=False)


# ─────────────────────────────────────────────
# TREND DATA (month by month per vendor)
# ─────────────────────────────────────────────

def get_vendor_trends() -> pd.DataFrame:
    df = load_fe_data()

    rows = []
    for (month, vendor), grp in df.groupby(["month", "Supplier"]):
        closed     = grp[grp["CLOSURE STATUS"] == "TASK CLOSE"]
        total      = len(grp)
        close_rate = round(len(closed) / total * 100, 1) if total else 0
        ta_pct     = round((grp["Task Acceptance"].str.upper() == "MET").sum() / total * 100, 1)

        rows.append({
            "month"            : month,
            "vendor"           : vendor,
            "total_jobs"       : total,
            "closure_rate_pct" : close_rate,
            "task_acceptance_pct": ta_pct,
            "avg_cost_usd"     : round(grp["Converted to USD"].mean(), 1),
        })

    trend_df = pd.DataFrame(rows)
    trend_df["month_dt"] = pd.to_datetime(trend_df["month"], format="%b-%Y", errors="coerce")
    return trend_df.sort_values("month_dt")


# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────

def get_fe_alerts(country: str = None) -> list:
    vendor_df = get_vendor_scorecard(country)

    if vendor_df.empty:
        return []

    alerts = []

    THRESHOLDS = {
        "closure_rate_pct"      : {"min": 70,  "label": "Closure rate below 70%"},
        "task_acceptance_pct"   : {"min": 70,  "label": "Task acceptance SLA below 70%"},
        "fe_closure_pct"        : {"min": 70,  "label": "FE closure SLA below 70%"},
        "avg_duration_hrs"      : {"max": 10,  "label": "Average job duration above 10 hours"},
        "avg_cost_usd"          : {"max": 800, "label": "Average job cost above $800"},
    }

    for _, row in vendor_df.iterrows():
        for col, rules in THRESHOLDS.items():
            val = row[col]
            if "min" in rules and val < rules["min"]:
                gap = rules["min"] - val
                pct = (gap / rules["min"]) * 100
                severity = "High" if pct > 25 else "Medium" if pct > 10 else "Low"
                alerts.append({
                    "vendor"    : row["vendor"],
                    "issue"     : rules["label"],
                    "actual"    : round(val, 1),
                    "threshold" : rules["min"],
                    "severity"  : severity,
                })
            if "max" in rules and val > rules["max"]:
                gap = val - rules["max"]
                pct = (gap / rules["max"]) * 100
                severity = "High" if pct > 25 else "Medium" if pct > 10 else "Low"
                alerts.append({
                    "vendor"    : row["vendor"],
                    "issue"     : rules["label"],
                    "actual"    : round(val, 1),
                    "threshold" : rules["max"],
                    "severity"  : severity,
                })

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    alerts.sort(key=lambda x: severity_order[x["severity"]])
    return alerts


# ─────────────────────────────────────────────
# HELPER — dropdown options
# ─────────────────────────────────────────────

def get_fe_countries() -> list:
    df = load_fe_data()
    return ["All"] + sorted(df["Customer location (Country)"].unique().tolist())


def get_fe_vendors() -> list:
    df = load_fe_data()
    return ["All"] + sorted(df["Supplier"].unique().tolist())


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing fe_filter.py...\n")

    print("Vendor Scorecard:")
    print(get_vendor_scorecard().to_string(index=False))

    print("\nTop FEs:")
    print(get_fe_scorecard().head(5).to_string(index=False))

    print("\nAlerts:")
    for a in get_fe_alerts():
        print(f"  [{a['severity']}] {a['vendor']} — {a['issue']} (Actual: {a['actual']})")