import os
import pandas as pd
import numpy as np

# Resolve paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "aggregated")

FILES = {
    "dom_carrier": os.path.join(RAW_DIR, "domestic", "carrier.csv"),
    "dom_city": os.path.join(RAW_DIR, "domestic", "city.csv"),
    "intl_carrier": os.path.join(RAW_DIR, "international", "carrier.csv"),
    "intl_city": os.path.join(RAW_DIR, "international", "city.csv"),
    "daily": os.path.join(RAW_DIR, "daily.csv"),
}

def audit_dataframe(name, path):
    print("=" * 88)
    print(f"AUDIT REPORT: {name.upper()}  |  {os.path.relpath(path, BASE_DIR)}")
    print("=" * 88)
    if not os.path.exists(path):
        print(f"  [ERROR] File not found at: {path}\n")
        return None

    df = pd.read_csv(path)
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Exact Duplicate Rows: {df.duplicated().sum()}\n")

    # 1. Column-level summary: dtype, nulls, zeros, min, max
    summary = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isna().sum())
        is_num = pd.api.types.is_numeric_dtype(df[col])
        zeros = int((df[col] == 0).sum()) if is_num else "-"
        min_val = f"{df[col].min():,.2f}" if is_num and pd.notna(df[col].min()) else "-"
        max_val = f"{df[col].max():,.2f}" if is_num and pd.notna(df[col].max()) else "-"
        n_unique = int(df[col].nunique(dropna=True))
        summary.append({
            "Column": col,
            "Dtype": dtype,
            "Nulls": nulls,
            "Zeros": zeros,
            "Unique": n_unique,
            "Min": min_val,
            "Max": max_val,
        })
    print(pd.DataFrame(summary).to_string(index=False))
    print()

    # 2. Text hygiene check: leading/trailing spaces & casing splits
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        s = df[col].dropna().astype(str)
        ws_issues = int((s != s.str.strip()).sum())
        unique_raw = s.nunique()
        unique_norm = s.str.strip().str.upper().nunique()
        if ws_issues > 0 or unique_raw != unique_norm:
            print(f"  [TEXT WARNING] '{col}': {ws_issues} whitespace issues | "
                  f"{unique_raw} raw unique vs {unique_norm} normalized unique")

    # 3. Domain-specific checks
    if name == "dom_carrier" and "Type" in df.columns:
        print("  [Distinct Type Values]:", df["Type"].value_counts(dropna=False).to_dict())

    if "Airline" in df.columns:
        airlines = sorted(df["Airline"].dropna().astype(str).str.strip().unique())
        print(f"  [Unique Airlines ({len(airlines)})]: {airlines}\n")

    if name == "daily" and "Domestic (Departing Pax)" in df.columns:
        col = "Domestic (Departing Pax)"
        non_zero = df[df[col] > 0][col]
        if len(non_zero) > 0:
            print(f"  [Daily Pax > 0]: count={len(non_zero):,}, min={non_zero.min():,.2f}, "
                  f"median={non_zero.median():,.2f}, mean={non_zero.mean():,.2f}, max={non_zero.max():,.2f}")
        print(f"  [Daily Pax == 0 or Null]: {(df[col].isna() | (df[col] == 0)).sum():,} rows")

    print("\n")
    return df

if __name__ == "__main__":
    for name, path in FILES.items():
        audit_dataframe(name, path)