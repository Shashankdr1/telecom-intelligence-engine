# regenerate_data.py
# Run this once to regenerate your CSV files with countries + new service types

import pandas as pd
import random

random.seed(42)

COUNTRIES     = ["India", "UAE", "UK", "USA", "Singapore", "Germany", "Australia"]
SERVICE_TYPES = [
    "Fiber Broadband", "Leased Line", "MPLS", "4G/5G Backhaul", "SD-WAN",
    "Dark Fiber", "VoIP", "IoT Connectivity", "Dedicated Internet Access"
]
MONTHS = pd.date_range(start="2024-01-01", periods=12, freq="MS").strftime("%Y-%m").tolist()

CARRIER_NAMES = [
    "SwiftLink Telecom", "NovaCom Networks", "PeakConnect Ltd",
    "BluePath Carriers", "ZenithWave", "TrustLine Communications",
    "BridgeNet Solutions", "ClearPath Telecom", "OmegaFiber",
    "StarRoute Networks", "EchoConnect", "VelocityNet",
    "PrimeLane Carriers", "AxisLink Telecom", "HorizonNet"
]

SUPPLIER_NAMES = [
    "TechEquip Pvt Ltd", "GlobalParts Supply", "NetGear Wholesale",
    "CircuitWorld", "FiberCore Supplies", "InfraVend Solutions",
    "PrecisionHardware", "ConnectParts India", "SwiftVend Tech",
    "AlliedSupplies Co", "OptiNetwork Parts", "BandwidthEquip"
]

# ── CARRIERS ──────────────────────────────────
carrier_rows = []

for carrier_id, name in enumerate(CARRIER_NAMES, start=1):
    country       = random.choice(COUNTRIES)
    service_types = random.sample(SERVICE_TYPES, k=random.randint(3, 5))
    quality_tier  = random.choice(["high", "medium", "low"])

    for month in MONTHS:
        for service in service_types:

            if quality_tier == "high":
                sla_adherence    = round(random.uniform(88, 99), 1)
                actual_lead_time = random.randint(5, 20) + random.randint(-1, 3)
                delay_rate       = round(random.uniform(1, 10), 1)
                penalty_events   = random.randint(0, 2)
            elif quality_tier == "medium":
                sla_adherence    = round(random.uniform(72, 88), 1)
                actual_lead_time = random.randint(5, 20) + random.randint(0, 7)
                delay_rate       = round(random.uniform(10, 25), 1)
                penalty_events   = random.randint(1, 6)
            else:
                sla_adherence    = round(random.uniform(50, 72), 1)
                actual_lead_time = random.randint(5, 20) + random.randint(3, 15)
                delay_rate       = round(random.uniform(25, 55), 1)
                penalty_events   = random.randint(4, 15)

            promised_lead_time = random.randint(5, 20)
            actual_lead_time   = max(1, actual_lead_time)
            jobs_completed     = random.randint(10, 80)

            carrier_rows.append({
                "carrier_id"              : f"C{carrier_id:03}",
                "carrier_name"            : name,
                "country"                 : country,
                "service_type"            : service,
                "month"                   : month,
                "sla_adherence_pct"       : sla_adherence,
                "promised_lead_time_days" : promised_lead_time,
                "actual_lead_time_days"   : actual_lead_time,
                "install_delay_rate_pct"  : delay_rate,
                "jobs_completed"          : jobs_completed,
                "sla_penalty_events"      : penalty_events,
                "quality_tier"            : quality_tier,
            })

carriers_df = pd.DataFrame(carrier_rows)


# ── SUPPLIERS ─────────────────────────────────
supplier_rows = []

for supplier_id, name in enumerate(SUPPLIER_NAMES, start=1):
    service_types = random.sample(SERVICE_TYPES, k=random.randint(3, 5))
    quality_tier  = random.choice(["high", "medium", "low"])

    for month in MONTHS:
        for service in service_types:

            if quality_tier == "high":
                cost_index       = round(random.uniform(0.85, 1.10), 2)
                quality_score    = round(random.uniform(85, 99), 1)
                fulfillment_rate = round(random.uniform(90, 100), 1)
                billing_accuracy = round(random.uniform(92, 100), 1)
                dispute_count    = random.randint(0, 2)
            elif quality_tier == "medium":
                cost_index       = round(random.uniform(1.00, 1.25), 2)
                quality_score    = round(random.uniform(68, 85), 1)
                fulfillment_rate = round(random.uniform(74, 90), 1)
                billing_accuracy = round(random.uniform(78, 92), 1)
                dispute_count    = random.randint(1, 5)
            else:
                cost_index       = round(random.uniform(1.15, 1.60), 2)
                quality_score    = round(random.uniform(45, 68), 1)
                fulfillment_rate = round(random.uniform(50, 74), 1)
                billing_accuracy = round(random.uniform(55, 78), 1)
                dispute_count    = random.randint(3, 12)

            orders_handled = random.randint(5, 50)

            supplier_rows.append({
                "supplier_id"          : f"S{supplier_id:03}",
                "supplier_name"        : name,
                "service_type"         : service,
                "month"                : month,
                "cost_index"           : cost_index,
                "quality_score"        : quality_score,
                "fulfillment_rate_pct" : fulfillment_rate,
                "billing_accuracy_pct" : billing_accuracy,
                "dispute_count"        : dispute_count,
                "orders_handled"       : orders_handled,
                "quality_tier"         : quality_tier,
            })

suppliers_df = pd.DataFrame(supplier_rows)

# ── SAVE ──────────────────────────────────────
carriers_df.to_csv("data/carriers.csv",  index=False)
suppliers_df.to_csv("data/suppliers.csv", index=False)

print(f"✅ Carriers  : {len(carriers_df)} rows | {carriers_df['carrier_id'].nunique()} carriers | Countries: {sorted(carriers_df['country'].unique())}")
print(f"✅ Suppliers : {len(suppliers_df)} rows | {suppliers_df['supplier_id'].nunique()} suppliers")
print(f"✅ Services  : {sorted(carriers_df['service_type'].unique())}")
print("✅ Files saved to data/ folder")