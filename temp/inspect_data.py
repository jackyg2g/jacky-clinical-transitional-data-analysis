"""
Inspect the Excel file: G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx
Lists sheet names, shapes, columns, first 20 rows, dtypes, and basic statistics.
"""

import pandas as pd
import sys

FILE_PATH = "/Users/jacky/Documents/jacky-clinical-transitional-data-analysis/reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 25)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 60)

xls = pd.ExcelFile(FILE_PATH, engine='openpyxl')

print("=" * 80)
print(f"FILE: {FILE_PATH}")
print(f"NUMBER OF SHEETS: {len(xls.sheet_names)}")
print(f"SHEET NAMES: {xls.sheet_names}")
print("=" * 80)

for sheet_name in xls.sheet_names:
    print(f"\n{'#' * 80}")
    print(f"SHEET: '{sheet_name}'")
    print(f"{'#' * 80}")

    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    print(f"\nRAW SHAPE (no header): {df.shape[0]} rows x {df.shape[1]} columns")

    # Show first 5 raw rows to understand header structure
    print(f"\n--- First 5 raw rows (to understand header structure) ---")
    print(df.head(5).to_string())

    # Now read with header
    df_h = pd.read_excel(xls, sheet_name=sheet_name)
    print(f"\nSHAPE (with header): {df_h.shape[0]} rows x {df_h.shape[1]} columns")

    print(f"\n--- Column Names ({len(df_h.columns)}) ---")
    for i, col in enumerate(df_h.columns):
        print(f"  [{i}] {col}")

    print(f"\n--- Data Types ---")
    print(df_h.dtypes.to_string())

    print(f"\n--- First 20 rows ---")
    print(df_h.head(20).to_string())

    # Basic statistics for numeric columns
    numeric_cols = df_h.select_dtypes(include='number').columns
    if len(numeric_cols) > 0:
        print(f"\n--- Basic Statistics (numeric columns) ---")
        print(df_h[numeric_cols].describe().to_string())

    # Non-null counts
    print(f"\n--- Non-null counts ---")
    print(df_h.count().to_string())

    # Unique value counts for object columns (first 10 unique values)
    obj_cols = df_h.select_dtypes(include='object').columns
    if len(obj_cols) > 0:
        print(f"\n--- Unique values for text columns ---")
        for col in obj_cols:
            nunique = df_h[col].nunique()
            sample_vals = df_h[col].dropna().unique()[:10]
            print(f"  '{col}': {nunique} unique values. Samples: {list(sample_vals)}")

    print()

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
