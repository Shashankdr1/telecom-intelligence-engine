# engine/fe_scorer.py
# Calls Groq AI to recommend the best FE vendor and engineer for a job

import json
import sys
import os
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers   import get_groq_api_key
from engine.fe_filter import get_vendor_scorecard, get_fe_scorecard, get_fe_alerts


def get_client():
    return Groq(api_key=get_groq_api_key())


def build_fe_prompt(country, expected_days, vendor_df, fe_df):
    vendor_text = vendor_df.to_string(index=False)
    fe_text     = fe_df.head(10).to_string(index=False)

    prompt = f"""
You are an expert Field Engineer (FE) Operations Analyst for a telecom managed services company.

A new field engineering job has come in:
- Country          : {country}
- Expected completion: within {expected_days} days

Below is the performance data for FE vendors and individual engineers (last 3 months).

=== VENDOR PERFORMANCE ===
{vendor_text}

Column definitions:
- closure_rate_pct       : % of jobs successfully closed (higher is better)
- task_acceptance_pct    : % of task acceptance SLA met (higher is better)
- fe_closure_pct         : % of FE closure SLA met (higher is better)
- avg_duration_hrs       : average hours per job (lower is better)
- avg_cost_usd           : average job cost in USD (lower is better)
- avg_cost_optimization  : average savings achieved per job (higher is better)
- total_saving_usd       : total savings in last 3 months (higher is better)

=== TOP INDIVIDUAL FEs ===
{fe_text}

Column definitions:
- closure_rate_pct    : % of jobs closed successfully (higher is better)
- task_acceptance_pct : % of SLA met on task acceptance (higher is better)
- fe_closure_pct      : % of SLA met on FE closure (higher is better)
- avg_duration_hrs    : average hours per job (lower is better)
- avg_cost_usd        : average job cost in USD (lower is better)

=== YOUR TASK ===
Analyze the data and recommend:

1. PRIMARY VENDOR   : Best vendor for this job with score out of 100 and reasoning
2. BACKUP VENDOR    : Second best vendor as fallback
3. PRIMARY FE       : Best individual field engineer with score and reasoning
4. BACKUP FE        : Second best individual field engineer
5. RISK ALERTS      : Any serious concerns about vendor or FE performance
6. COST INSIGHT     : Observations about cost efficiency and savings
7. ACTION PLAN      : Short paragraph advising the operations team

Scoring weights:
- Vendors : closure rate 35%, task acceptance 25%, FE closure 20%, cost efficiency 20%
- FEs     : closure rate 40%, task acceptance 30%, FE closure 20%, duration 10%

IMPORTANT: Respond ONLY in valid JSON. No extra text.

{{
  "primary_vendor": {{
    "vendor"    : "",
    "score"     : 0,
    "reasoning" : ""
  }},
  "backup_vendor": {{
    "vendor"    : "",
    "score"     : 0,
    "reasoning" : ""
  }},
  "primary_fe": {{
    "fe_name"   : "",
    "vendor"    : "",
    "score"     : 0,
    "reasoning" : ""
  }},
  "backup_fe": {{
    "fe_name"   : "",
    "vendor"    : "",
    "score"     : 0,
    "reasoning" : ""
  }},
  "risk_alerts"  : [],
  "cost_insight" : "",
  "action_plan"  : ""
}}
"""
    return prompt.strip()


def get_fe_recommendation(country: str, expected_days: int = 30) -> dict:
    vendor_df = get_vendor_scorecard(country)
    fe_df     = get_fe_scorecard(country)

    if vendor_df.empty:
        return {"error": f"No FE vendor data found for {country}."}

    if fe_df.empty:
        return {"error": f"No individual FE data found for {country}."}

    prompt   = build_fe_prompt(country, expected_days, vendor_df, fe_df)
    client   = get_client()

    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {
                "role"    : "system",
                "content" : "You are a telecom FE operations analyst. Always respond in valid JSON only."
            },
            {
                "role"    : "user",
                "content" : prompt
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


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing fe_scorer.py — calling Groq API...\n")

    result = get_fe_recommendation(country="All", expected_days=30)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"PRIMARY VENDOR : {result['primary_vendor']['vendor']} (Score: {result['primary_vendor']['score']})")
        print(f"  Reasoning    : {result['primary_vendor']['reasoning']}\n")
        print(f"BACKUP VENDOR  : {result['backup_vendor']['vendor']} (Score: {result['backup_vendor']['score']})")
        print(f"  Reasoning    : {result['backup_vendor']['reasoning']}\n")
        print(f"PRIMARY FE     : {result['primary_fe']['fe_name']} ({result['primary_fe']['vendor']}) Score: {result['primary_fe']['score']}")
        print(f"  Reasoning    : {result['primary_fe']['reasoning']}\n")
        print(f"BACKUP FE      : {result['backup_fe']['fe_name']} ({result['backup_fe']['vendor']}) Score: {result['backup_fe']['score']}")
        print(f"  Reasoning    : {result['backup_fe']['reasoning']}\n")
        print(f"RISK ALERTS    :")
        for a in result["risk_alerts"]:
            print(f"  - {a}")
        print(f"\nCOST INSIGHT   : {result['cost_insight']}")
        print(f"\nACTION PLAN    : {result['action_plan']}")