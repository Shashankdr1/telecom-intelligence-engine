# utils/helpers.py

import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR       = os.path.join(BASE_DIR, "data")
CARRIERS_PATH  = os.path.join(DATA_DIR, "carriers.csv")
SUPPLIERS_PATH = os.path.join(DATA_DIR, "suppliers.csv")


def load_carriers():
    df = pd.read_csv(CARRIERS_PATH)
    df["carrier_name"] = df["carrier_name"].str.strip()
    df["country"]      = df["country"].str.strip()
    df["service_type"] = df["service_type"].str.strip()
    return df


def load_suppliers():
    df = pd.read_csv(SUPPLIERS_PATH)
    df["supplier_name"] = df["supplier_name"].str.strip()
    df["service_type"]  = df["service_type"].str.strip()
    return df


def get_countries():
    df = load_carriers()
    return sorted(df["country"].unique().tolist())


def get_service_types():
    df = load_carriers()
    return sorted(df["service_type"].unique().tolist())


def get_groq_api_key():
    # Works locally (.env) and on Streamlit Cloud (st.secrets)
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except Exception:
        key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not found.")
    return key


if __name__ == "__main__":
    print("Testing helpers.py...\n")
    carriers  = load_carriers()
    suppliers = load_suppliers()
    print(f"Carriers loaded  : {len(carriers)} rows, {carriers['carrier_id'].nunique()} unique carriers")
    print(f"Suppliers loaded : {len(suppliers)} rows, {suppliers['supplier_id'].nunique()} unique suppliers")
    print(f"\nCountries available     : {get_countries()}")
    print(f"Service types available : {get_service_types()}")
    try:
        key = get_groq_api_key()
        print(f"\nGroq API key found : {key[:8]}...")
    except ValueError as e:
        print(f"\nWarning: {e}")