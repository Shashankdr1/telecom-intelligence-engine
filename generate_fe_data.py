# generate_fe_data.py
# Generates a sample FE dataset matching your real Google Sheet structure

import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# ── CONFIG ──────────────────────────────────
VENDORS   = ["SGS", "Neeco", "NSC"]
COUNTRIES = ["Germany", "Kenya", "Indonesia", "China", "India", "UAE", "UK", "USA", "Singapore", "Australia"]
CUSTOMERS = [
    "Vodafone Italia", "Hilton Hotels", "Seven For All Mankind",
    "SGS S.A.", "Deutsche Telekom", "Airtel Africa",
    "Cisco Systems", "Nokia Networks", "Ericsson", "Huawei"
]
FE_BY_VENDOR = {
    "SGS"  : ["Ismail Ahmed", "Ronald Yau", "Fatihaqul Ihsan", "Raj Kumar", "Chen Wei",
               "Priya Singh", "Omar Hassan", "Lucas Silva", "Anna Kowalski", "James Osei"],
    "Neeco": ["Joel Macharia", "Maria Santos", "Ivan Petrov", "Yuki Tanaka", "Amir Khan",
               "Fatima Al-Rashid", "Carlos Mendez", "Sophie Martin", "Ali Hassan", "Ngozi Adeyemi"],
    "NSC"  : ["David Kimani", "Sarah Johnson", "Mohammed Al-Farsi", "Lin Xiaoming", "Amara Diallo",
               "Elena Ivanova", "Pedro Alves", "Nadia Benali", "Kwame Mensah", "Rania Mostafa"]
}
REQUESTORS  = ["Renuka", "Anandhy", "Sonali", "Supriya", "Priya", "Rahul", "Deepa"]
CLOSURE_STATUSES = ["TASK CLOSE", "OPEN TASK", "CANCELLED"]
PROJECT_TYPES    = ["BAU", "Project"]
SLA_OPTIONS      = ["MET", "Not Met"]

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_time():
    hour   = random.randint(8, 18)
    minute = random.choice([0, 15, 30, 45])
    return f"{hour:02d}:{minute:02d}"

rows = []
start_date = datetime(2024, 1, 1)
end_date   = datetime(2024, 12, 31)

for i in range(1335):
    vendor      = random.choice(VENDORS)
    fe_name     = random.choice(FE_BY_VENDOR[vendor])
    country     = random.choice(COUNTRIES)
    customer    = random.choice(CUSTOMERS)
    received_dt = random_date(start_date, end_date)
    accept_dt   = received_dt + timedelta(days=random.randint(0, 2))
    install_dt  = accept_dt  + timedelta(days=random.randint(1, 10))
    close_dt    = install_dt + timedelta(days=random.randint(0, 5))
    month       = received_dt.strftime("%b-%Y")

    # Quality tier per vendor (hidden driver)
    quality = {"SGS": "high", "Neeco": "medium", "NSC": "low"}[vendor]

    # Duration
    if quality == "high":
        duration     = round(random.uniform(2, 6), 1)
        add_hrs      = round(random.uniform(0, 1), 1)
        chr_value    = round(random.uniform(300, 600), 2)
        sla_task     = random.choices(["MET", "Not Met"], weights=[85, 15])[0]
        sla_fe       = random.choices(["MET", "Not Met"], weights=[85, 15])[0]
        sla_closer   = random.choices(["MET", "Not Met"], weights=[80, 20])[0]
        closure      = random.choices(CLOSURE_STATUSES, weights=[80, 15, 5])[0]
        cost_opt     = round(random.uniform(50, 200), 2)
    elif quality == "medium":
        duration     = round(random.uniform(4, 10), 1)
        add_hrs      = round(random.uniform(1, 3), 1)
        chr_value    = round(random.uniform(400, 800), 2)
        sla_task     = random.choices(["MET", "Not Met"], weights=[65, 35])[0]
        sla_fe       = random.choices(["MET", "Not Met"], weights=[65, 35])[0]
        sla_closer   = random.choices(["MET", "Not Met"], weights=[60, 40])[0]
        closure      = random.choices(CLOSURE_STATUSES, weights=[65, 25, 10])[0]
        cost_opt     = round(random.uniform(20, 100), 2)
    else:
        duration     = round(random.uniform(6, 16), 1)
        add_hrs      = round(random.uniform(2, 6), 1)
        chr_value    = round(random.uniform(500, 1200), 2)
        sla_task     = random.choices(["MET", "Not Met"], weights=[45, 55])[0]
        sla_fe       = random.choices(["MET", "Not Met"], weights=[45, 55])[0]
        sla_closer   = random.choices(["MET", "Not Met"], weights=[40, 60])[0]
        closure      = random.choices(CLOSURE_STATUSES, weights=[50, 35, 15])[0]
        cost_opt     = round(random.uniform(0, 50), 2)

    basic_rate   = round(chr_value * 0.6, 2)
    final_charge = round(chr_value - cost_opt, 2)
    basic_saving = round(chr_value - final_charge, 2)

    in_time  = random_time()
    out_hour = int(in_time.split(":")[0]) + int(duration)
    out_time = f"{min(out_hour, 23):02d}:{in_time.split(':')[1]}"

    rows.append({
        "CHR/ IB Item ID"                        : f"CHR{str(1000000 + i).zfill(9)}",
        "Customer Name"                           : customer,
        "Site Name"                               : f"{customer} - {country}",
        "Customer location (Country)"             : country,
        "Project/ BAU"                            : random.choice(PROJECT_TYPES),
        "FEB Reference"                           : f"FEB{random.randint(1000000000, 9999999999)}",
        "Task Received Date"                      : received_dt.strftime("%m/%d/%Y"),
        "month"                                   : month,
        "Task Accept Date"                        : accept_dt.strftime("%m/%d/%Y"),
        "Request place date"                      : accept_dt.strftime("%m/%d/%Y"),
        "Task close date"                         : close_dt.strftime("%m/%d/%Y"),
        "Date of Install"                         : install_dt.strftime("%m/%d/%Y"),
        "INSTALL TIME"                            : in_time,
        "CHR Value"                               : chr_value,
        "Curr."                                   : "USD",
        "Converted to USD"                        : chr_value,
        "Duration Hour"                           : duration,
        "Additional hrs"                          : add_hrs,
        "quote received"                          : accept_dt.strftime("%m/%d/%Y"),
        "Neeco- Basic"                            : basic_rate if vendor == "Neeco" else 0,
        "Neeco - addi"                            : add_hrs * 30 if vendor == "Neeco" else 0,
        "SGS-Basic"                               : basic_rate if vendor == "SGS" else 0,
        "SGS - addi"                              : add_hrs * 30 if vendor == "SGS" else 0,
        "NSC- Basic"                              : basic_rate if vendor == "NSC" else 0,
        "Travel/cable /nuts"                      : round(random.uniform(10, 80), 2),
        "NSC - addi"                              : add_hrs * 30 if vendor == "NSC" else 0,
        "Supplier"                                : vendor,
        "Basic Hrs"                               : duration,
        "Additional hrs "                         : add_hrs,
        "Curr. "                                  : "USD",
        "Basic saving"                            : basic_saving,
        "Cost optimization"                       : cost_opt,
        "Additional hrs  "                        : add_hrs,
        "Final Charges"                           : final_charge,
        "FE received Date- Vendor"                : accept_dt.strftime("%m/%d/%Y"),
        "FE details shared - Requestor"           : (accept_dt + timedelta(days=1)).strftime("%m/%d/%Y"),
        "FE Name"                                 : fe_name,
        "FE Contact No."                          : f"+{random.randint(1,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
        "Task Regarding"                          : "FE detail Received",
        "Requestor name"                          : random.choice(REQUESTORS),
        "PO NO"                                   : random.randint(4500000000, 4599999999),
        "Remarks"                                 : "",
        "IN TIME"                                 : in_time,
        "OUT TIME"                                : out_time,
        "closed"                                  : close_dt.strftime("%m/%d/%Y"),
        "Quote ETA"                               : random.randint(1, 5),
        "Request received, validated - Accepted/Rejected": random.choices(["MET", "Not Met"], weights=[75, 25])[0],
        "Order placing to vendors"                : random.choices(["MET", "Not Met"], weights=[70, 30])[0],
        "Expected ETA from vendor"                : random.choices(["MET", "Not Met"], weights=[70, 30])[0],
        "Provide ETA & FE details to internal team": random.choices(["MET", "Not Met"], weights=[72, 28])[0],
        "Closer Measurement"                      : sla_closer,
        "Task Acceptance"                         : sla_task,
        "FE closure"                              : sla_fe,
        "quote received date"                     : accept_dt.strftime("%m/%d/%Y"),
        "SVR Received date"                       : close_dt.strftime("%m/%d/%Y"),
        "PO Created date"                         : accept_dt.strftime("%m/%d/%Y"),
        "CLOSURE STATUS"                          : closure,
    })

df = pd.DataFrame(rows)
df.to_csv("data/fe_data.csv", index=False)

print(f"✅ FE dataset generated: {len(df)} rows")
print(f"   Vendors   : {df['Supplier'].value_counts().to_dict()}")
print(f"   Countries : {sorted(df['Customer location (Country)'].unique())}")
print(f"   FE Names  : {df['FE Name'].nunique()} unique engineers")
print(f"   Months    : {df['month'].min()} → {df['month'].max()}")
print(f"   Closure   : {df['CLOSURE STATUS'].value_counts().to_dict()}")