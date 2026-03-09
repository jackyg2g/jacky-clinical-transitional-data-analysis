"""
Inspect sample.xlsx: list sheets, columns, shapes, data types, unique categorical values.
"""
import pandas as pd
import sys

FILE = "/Users/jacky/Documents/jacky-clinical-transitional-data-analysis/reference/raw-data-yance/sample.xlsx"

xls = pd.ExcelFile(FILE, engine="openpyxl")
print("=" * 80)
print(f"FILE: {FILE}")
print(f"SHEET NAMES: {xls.sheet_names}")
print(f"NUMBER OF SHEETS: {len(xls.sheet_names)}")
print("=" * 80)

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    print(f"\n{'#' * 80}")
    print(f"SHEET: '{sheet}'")
    print(f"SHAPE: {df.shape}  ({df.shape[0]} rows x {df.shape[1]} columns)")
    print(f"{'#' * 80}")

    # Column names and dtypes
    print(f"\n--- COLUMNS & DTYPES ({len(df.columns)} columns) ---")
    for i, col in enumerate(df.columns):
        non_null = df[col].notna().sum()
        print(f"  [{i}] {col!r:40s}  dtype={str(df[col].dtype):15s}  non-null={non_null}/{len(df)}")

    # First 20 rows
    print(f"\n--- FIRST 20 ROWS ---")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 60)
    pd.set_option('display.width', 300)
    pd.set_option('display.max_rows', 25)
    print(df.head(20).to_string(index=True))

    # Sample values (first 5 non-null) per column
    print(f"\n--- SAMPLE VALUES (up to 5 non-null per column) ---")
    for col in df.columns:
        vals = df[col].dropna().head(5).tolist()
        print(f"  {col!r}: {vals}")

    # Unique values for likely categorical columns (object dtype or fewer than 50 unique values)
    print(f"\n--- UNIQUE VALUES FOR KEY CATEGORICAL COLUMNS ---")
    for col in df.columns:
        n_unique = df[col].nunique()
        # Show uniques for object columns or columns with few unique values
        if df[col].dtype == 'object' or n_unique <= 50:
            uniques = sorted(df[col].dropna().unique().tolist(), key=lambda x: str(x))
            print(f"  {col!r} ({n_unique} unique): {uniques}")
        else:
            print(f"  {col!r} ({n_unique} unique): [numeric, too many to list] range=[{df[col].min()}, {df[col].max()}]")

    # Basic stats for numeric columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        print(f"\n--- NUMERIC SUMMARY ---")
        print(df[numeric_cols].describe().to_string())

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
