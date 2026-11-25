import os
import re
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "aggregated")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

# Aggregate summary labels embedded in DGCA Airline/Country columns (removed to prevent double counting)
AGGREGATE_LABELS = {
    "TOTAL DOMESTIC",
    "TOTAL INTERNATIONAL",
    "TOTAL",
    "GRAND TOTAL",
}

# Canonical airline mapping fixing DGCA spelling typos & entity rebrands
AIRLINE_MAP = {
    "INDIGO": "IndiGo",
    "INTERGLOBE AVIATION": "IndiGo",
    "AIR INDIA": "Air India",
    "AIR INDIA LTD": "Air India",
    "AIR INDIA EXPRESS": "Air India Express",
    "AIX CONNECT": "AIX Connect",
    "AIRASIA INDIA": "AirAsia India",
    "AIR ASIA": "AirAsia",
    "AIR ASIA BERHAD": "AirAsia Berhad",
    "AIR ASIA X": "AirAsia X",
    "VISTARA": "Vistara",
    "VISTARA AIRLINES": "Vistara",
    "TATA SIA AIRLINES": "Vistara",
    "SPICEJET": "SpiceJet",
    "AKASA AIR": "Akasa Air",
    "GO FIRST": "Go First",
    "GO AIR": "Go First",
    "GOAIR": "Go First",
    "ALLIANCE AIR": "Alliance Air",
    "STAR AIR": "Star Air",
    "FLYBIG": "FlyBig",
    "TRUJET": "TruJet",
    "JET AIRWAYS": "Jet Airways",
    "JETLITE": "JetLite",
    "BLUE DART AVIATION": "Blue Dart Aviation",
    "QATAR AIRWAYS": "Qatar Airways",
    "QATAR AIRWATYS": "Qatar Airways",
    "SRILANKAN AIRWAYS": "SriLankan Airlines",
    "SRILNKAN AIRWAYS": "SriLankan Airlines",
    "BUDDHA AIR": "Buddha Air",
    "BUDHHA AIR": "Buddha Air",
    "UGANDA AIRLINES": "Uganda Airlines",
    "UGANDA AIRLNES": "Uganda Airlines",
    "RWANDAIR": "RwandAir",
    "RWANDA AIR": "RwandAir",
    "ROYAL JORDANIAN": "Royal Jordanian",
    "SOUTHA AFRICAN AIRLINES": "South African Airways",
}

# Canonical country mapping for common DGCA international country naming variations
COUNTRY_MAP = {
    "UAE": "UNITED ARAB EMIRATES",
    "U.A.E.": "UNITED ARAB EMIRATES",
    "U.A.E": "UNITED ARAB EMIRATES",
    "UK": "UNITED KINGDOM",
    "U.K.": "UNITED KINGDOM",
    "U.K": "UNITED KINGDOM",
    "USA": "UNITED STATES",
    "U.S.A.": "UNITED STATES",
    "U.S.A": "UNITED STATES",
    "UNITED STATES OF AMERICA": "UNITED STATES",
    "KSA": "SAUDI ARABIA",
    "KINGDOM OF SAUDI ARABIA": "SAUDI ARABIA",
    "HONGKONG": "HONG KONG",
    "HONG KONG SAR": "HONG KONG",
    "REPUBLIC OF KOREA": "SOUTH KOREA",
    "KOREA": "SOUTH KOREA",
    "RUSSIAN FEDERATION": "RUSSIA",
    "VIET NAM": "VIETNAM",
    "TÜRKIYE": "TURKEY",
    "TURKIYE": "TURKEY",
}

def clean_text_series(s: pd.Series) -> pd.Series:
    return (
        s.astype("string")
        .str.replace(r"[\r\n\t]+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

def standardize_airline(s: pd.Series) -> pd.Series:
    cleaned = clean_text_series(s)
    upper_key = cleaned.str.upper()
    return upper_key.map(AIRLINE_MAP).fillna(cleaned)

def standardize_country(s: pd.Series) -> pd.Series:
    cleaned = clean_text_series(s).str.upper()
    return cleaned.map(COUNTRY_MAP).fillna(cleaned)

def normalize_year(s: pd.Series) -> pd.Series:
    yr = pd.to_numeric(s, errors="coerce")
    yr = np.where(yr < 100, yr + 2000, yr)
    return pd.Series(yr, index=s.index).astype("Int64")

def coerce_numeric(df: pd.DataFrame, exclude_cols: list) -> pd.DataFrame:
    for col in df.columns:
        if col not in exclude_cols:
            if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                cleaned_num = (
                    df[col]
                    .astype(str)
                    .str.replace("%", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )
                df[col] = pd.to_numeric(cleaned_num, errors="coerce")
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def clean_dom_carrier():
    path = os.path.join(RAW_DIR, "domestic", "carrier.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Type"] = clean_text_series(df["Type"])
    df["Airline"] = standardize_airline(df["Airline"])

    before_rows = len(df)
    df = df[~df["Airline"].str.upper().isin(AGGREGATE_LABELS)].copy()
    print(f"  [dom_carrier] Removed {before_rows - len(df)} aggregate 'Total' rows.")

    df["Year"] = normalize_year(df["Year"])
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Year", "Month", "Airline", "Type"]).copy()
    df = coerce_numeric(df, exclude_cols=["Type", "Airline", "Year", "Month"])

    if "Weight Load Factor" in df.columns:
        df.loc[df["Weight Load Factor"] > 100, "Weight Load Factor"] = np.nan

    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=df["Month"], day=1), errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df = df.drop_duplicates(subset=["Date", "Type", "Airline"], keep="last")
    df.to_csv(os.path.join(CLEAN_DIR, "fact_dom_carrier.csv"), index=False)
    print(f"[SAVED] fact_dom_carrier.csv -> {len(df):,} rows\n")

def clean_dom_city():
    path = os.path.join(RAW_DIR, "domestic", "city.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["City1"] = clean_text_series(df["City1"]).str.upper()
    df["City2"] = clean_text_series(df["City2"]).str.upper()
    df["Year"] = normalize_year(df["Year"])
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")

    df = df.dropna(subset=["Year", "Month", "City1", "City2"]).copy()
    df = coerce_numeric(df, exclude_cols=["City1", "City2", "Year", "Month"])

    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=df["Month"], day=1), errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df["Corridor"] = np.where(
        df["City1"] < df["City2"],
        df["City1"] + " - " + df["City2"],
        df["City2"] + " - " + df["City1"],
    )

    num_cols = [c for c in df.columns if c not in ["Year", "Month", "Date", "City1", "City2", "Corridor"]]
    df = df.groupby(["Year", "Month", "Date", "City1", "City2", "Corridor"], as_index=False)[num_cols].sum(min_count=1)

    df.to_csv(os.path.join(CLEAN_DIR, "fact_dom_city.csv"), index=False)
    print(f"[SAVED] fact_dom_city.csv -> {len(df):,} rows\n")

def clean_intl_carrier():
    path = os.path.join(RAW_DIR, "international", "carrier.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Airline"] = standardize_airline(df["Airline"])
    df = df[~df["Airline"].str.upper().isin(AGGREGATE_LABELS)].copy()

    df["Year"] = normalize_year(df["Year"])
    df["Quarter"] = pd.to_numeric(df["Quarter"].astype(str).str.extract(r"(\d+)")[0], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Year", "Quarter", "Airline"]).copy()

    df = coerce_numeric(df, exclude_cols=["Airline", "Year", "Quarter"])
    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=(df["Quarter"] - 1) * 3 + 1, day=1), errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    num_cols = [c for c in df.columns if c not in ["Year", "Quarter", "Date", "Airline"]]
    df = df.groupby(["Year", "Quarter", "Date", "Airline"], as_index=False)[num_cols].sum(min_count=1)

    df.to_csv(os.path.join(CLEAN_DIR, "fact_intl_carrier.csv"), index=False)
    print(f"[SAVED] fact_intl_carrier.csv -> {len(df):,} rows\n")

def clean_intl_city():
    path = os.path.join(RAW_DIR, "international", "city.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["City1"] = clean_text_series(df["City1"]).str.upper()
    df["City2"] = clean_text_series(df["City2"]).str.upper()

    df["Year"] = normalize_year(df["Year"])
    df["Quarter"] = pd.to_numeric(df["Quarter"].astype(str).str.extract(r"(\d+)")[0], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Year", "Quarter", "City1", "City2"]).copy()

    df = coerce_numeric(df, exclude_cols=["City1", "City2", "Year", "Quarter"])
    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=(df["Quarter"] - 1) * 3 + 1, day=1), errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df["Corridor"] = np.where(
        df["City1"] < df["City2"],
        df["City1"] + " - " + df["City2"],
        df["City2"] + " - " + df["City1"],
    )

    num_cols = [c for c in df.columns if c not in ["Year", "Quarter", "Date", "City1", "City2", "Corridor"]]
    df = df.groupby(["Year", "Quarter", "Date", "City1", "City2", "Corridor"], as_index=False)[num_cols].sum(min_count=1)

    df.to_csv(os.path.join(CLEAN_DIR, "fact_intl_city.csv"), index=False)
    print(f"[SAVED] fact_intl_city.csv -> {len(df):,} rows\n")

def clean_intl_country():
    path = os.path.join(RAW_DIR, "international", "country.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Identify the country column dynamically ('Country' or 'CountryName')
    country_col = next((c for c in df.columns if "country" in c.lower()), "Country")
    df[country_col] = standardize_country(df[country_col])

    before_rows = len(df)
    df = df[~df[country_col].isin(AGGREGATE_LABELS)].copy()
    if before_rows != len(df):
        print(f"  [intl_country] Removed {before_rows - len(df)} aggregate 'Total' rows.")

    df["Year"] = normalize_year(df["Year"])
    df["Quarter"] = pd.to_numeric(df["Quarter"].astype(str).str.extract(r"(\d+)")[0], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Year", "Quarter", country_col]).copy()

    df = coerce_numeric(df, exclude_cols=[country_col, "Year", "Quarter"])
    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=(df["Quarter"] - 1) * 3 + 1, day=1), errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    num_cols = [c for c in df.columns if c not in ["Year", "Quarter", "Date", country_col]]
    df = df.groupby(["Year", "Quarter", "Date", country_col], as_index=False)[num_cols].sum(min_count=1)

    df.to_csv(os.path.join(CLEAN_DIR, "fact_intl_country.csv"), index=False)
    print(f"[SAVED] fact_intl_country.csv -> {len(df):,} rows\n")

def clean_daily_moca():
    path = os.path.join(RAW_DIR, "daily.csv")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").copy()

    keep_prefixes = (
        "Date",
        "Domestic (",
        "International (",
        "Cargo (In MT)",
        "On Time Performance (",
        "Passenger Load Factor (",
        "Grievances (Received",
        "Grievances (Resolved",
        "Grievances (Pending",
        "Grievances (Baggage)",
        "Grievances (Refunds)",
        "Grievances (Check-In)",
        "Grievances (Security",
        "Grievances (Meals)",
        "Airports (",
        "UDAN (RCS)",
    )
    selected_cols = [c for c in df.columns if c.startswith(keep_prefixes)]
    df = df[selected_cols].copy()

    df = coerce_numeric(df, exclude_cols=["Date"])

    df = df.drop_duplicates(subset=["Date"], keep="last")
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    df.to_csv(os.path.join(CLEAN_DIR, "fact_daily_moca.csv"), index=False)
    print(f"[SAVED] fact_daily_moca.csv -> {len(df):,} rows x {len(df.columns)} columns\n")

if __name__ == "__main__":
    print("Running India Aviation Data Cleaning Pipeline...\n")
    clean_dom_carrier()
    clean_dom_city()
    clean_intl_carrier()
    clean_intl_city()
    clean_intl_country()
    clean_daily_moca()
    print("All 6 cleaned files exported to data/cleaned/ successfully.")