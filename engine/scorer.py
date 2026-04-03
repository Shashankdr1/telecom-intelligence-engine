# engine/scorer.py

import json
import sys
import os
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import get_groq_api_key
from engine.filter import filter_carriers, filter_suppliers


def get_client():
    return Groq(api_key=get_groq_api_key())


def build_prompt(country, service_type, expected_days, carriers_df, suppliers_df):
    carriers_text  = carriers_df.to_string(index=False)
    suppliers_text = suppliers_df.to_string(index=False)

    prompt = f"""
You are an expert Telecom Partner Performance Analyst working for a managed services company.

A new service request has come in with these requirements:
- Country              : {country}
- Service Type         : {service_type}
- Customer Expected    : Service delivery within {expected_days} days

Below is the historical performance data (last 3 months) for eligible carriers and suppliers.

=== CARRIER PERFORMANCE DATA ===
{carriers_text}

Column definitions:
- avg_sla_adherence    : % of jobs delivered within SLA window (higher is better)
- avg_lead_time_days   : average actual delivery time in days (lower is better, must be within {expected_days} days)
- avg_delay_rate       : % of jobs that had installation delays (lower is better)
- total_jobs           : total jobs handled in last 3 months (higher = more experienced)
- total_penalty_events : number of SLA breach penalties (lower is better)

=== SUPPLIER PERFORMANCE DATA ===
{suppliers_text}

Column definitions:
- avg_cost_index       : cost vs market average, 1.0 = market rate (lower is better)
- avg_quality_score    : equipment quality out of 100 (higher is better)
- avg_fulfillment_rate : % of ordered quantity delivered on time (higher is better)
- avg_billing_accuracy : % of invoices without errors (higher is better)
- total_disputes       : number of billing disputes in last 3 months (lower is better)

=== IMPORTANT DELIVERY CONSTRAINT ===
The customer expects delivery within {expected_days} days.
Carriers whose avg_lead_time_days exceeds {expected_days} days should be flagged as a delivery risk.
Prioritise carriers who can realistically meet this deadline.

=== YOUR TASK ===
Analyze the data and provide:
1. PRIMARY CARRIER   : Best carrier with score out of 100 and reasoning
2. BACKUP CARRIER    : Second best carrier as fallback
3. PRIMARY SUPPLIER  : Best supplier with score out of 100 and reasoning
4. BACKUP SUPPLIER   : Second best supplier as fallback
5. RISK ALERTS       : Serious concerns or red flags including delivery timeline risks
6. TREND INSIGHT     : Patterns or observations worth noting
7. ACTION PLAN       : Short paragraph advising what the team should do

Scoring weights for carriers  : SLA adherence 40%, lead time vs expected date 30%, delay rate 20%, penalty events 10%
Scoring weights for suppliers : quality score 35%, fulfillment rate 30%, billing accuracy 20%, cost index 15%

IMPORTANT: Respond ONLY in valid JSON format. No extra text before or after.
Use exactly this structure:

{{
  "primary_carrier": {{
    "carrier_id"   : "",
    "carrier_name" : "",
    "score"        : 0,
    "reasoning"    : ""
  }},
  "backup_carrier": {{
    "carrier_id"   : "",
    "carrier_name" : "",
    "score"        : 0,
    "reasoning"    : ""
  }},
  "primary_supplier": {{
    "supplier_id"   : "",
    "supplier_name" : "",
    "score"         : 0,
    "reasoning"     : ""
  }},
  "backup_supplier": {{
    "supplier_id"   : "",
    "supplier_name" : "",
    "score"         : 0,
    "reasoning"     : ""
  }},
  "risk_alerts"   : [],
  "trend_insight" : "",
  "action_plan"   : ""
}}
"""
    return prompt.strip()


def get_recommendation(country: str, service_type: str, expected_days: int = 30) -> dict:
    carriers_df  = filter_carriers(country, service_type)
    suppliers_df = filter_suppliers(service_type)

    if carriers_df.empty:
        return {"error": f"No carriers found for {service_type} in {country}."}

    if suppliers_df.empty:
        return {"error": f"No suppliers found for {service_type}."}

    prompt = build_prompt(country, service_type, expected_days, carriers_df, suppliers_df)

    client   = get_client()
    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {
                "role"   : "system",
                "content": "You are a telecom performance analyst. Always respond in valid JSON only."
            },
            {
                "role"   : "user",
                "content": prompt
            }
        ],
        temperature = 0.2,
        max_tokens  = 1500,
    )

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    return json.loads(raw_text)


if __name__ == "__main__":
    print("Testing scorer.py — calling Groq API...\n")

    country      = "India"
    service_type = "Fiber Broadband"
    expected_days = 30

    result = get_recommendation(country, service_type, expected_days)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"PRIMARY CARRIER  : {result['primary_carrier']['carrier_name']} (Score: {result['primary_carrier']['score']})")
        print(f"  Reasoning      : {result['primary_carrier']['reasoning']}\n")
        print(f"BACKUP CARRIER   : {result['backup_carrier']['carrier_name']} (Score: {result['backup_carrier']['score']})")
        print(f"  Reasoning      : {result['backup_carrier']['reasoning']}\n")
        print(f"PRIMARY SUPPLIER : {result['primary_supplier']['supplier_name']} (Score: {result['primary_supplier']['score']})")
        print(f"  Reasoning      : {result['primary_supplier']['reasoning']}\n")
        print(f"BACKUP SUPPLIER  : {result['backup_supplier']['supplier_name']} (Score: {result['backup_supplier']['score']})")
        print(f"  Reasoning      : {result['backup_supplier']['reasoning']}\n")
        print(f"RISK ALERTS      :")
        for alert in result["risk_alerts"]:
            print(f"  - {alert}")
        print(f"\nTREND INSIGHT    : {result['trend_insight']}")
        print(f"\nACTION PLAN      : {result['action_plan']}")