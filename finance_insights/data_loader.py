"""Load and parse Simplifi CSV exports."""

import os
import pandas as pd


# Expected columns from Simplifi CSV export
EXPECTED_COLUMNS = ["Date", "Payee", "Amount", "Category", "Account", "Tags", "Memo"]

# Common column name mappings for flexibility
COLUMN_ALIASES = {
    "date": "Date",
    "transaction date": "Date",
    "payee": "Payee",
    "description": "Payee",
    "merchant": "Payee",
    "name": "Payee",
    "amount": "Amount",
    "category": "Category",
    "account": "Account",
    "account name": "Account",
    "tags": "Tags",
    "tag": "Tags",
    "memo": "Memo",
    "note": "Memo",
    "notes": "Memo",
}


def load_csv(filepath):
    """Load a single CSV file and normalize column names."""
    df = pd.read_csv(filepath)

    # Normalize column names
    rename_map = {}
    for col in df.columns:
        lower = col.strip().lower()
        if lower in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[lower]
    df = df.rename(columns=rename_map)

    # Ensure required columns exist
    for col in ["Date", "Amount"]:
        if col not in df.columns:
            raise ValueError(f"CSV missing required column: {col}. Found: {list(df.columns)}")

    # Add missing optional columns
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[EXPECTED_COLUMNS]


def load_all_csvs(data_dir="data"):
    """Load all CSV files from the data directory and merge them."""
    csv_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:
        return None, []

    dfs = []
    loaded_files = []
    for filepath in csv_files:
        try:
            df = load_csv(filepath)
            dfs.append(df)
            loaded_files.append(os.path.basename(filepath))
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")

    if not dfs:
        return None, []

    combined = pd.concat(dfs, ignore_index=True)
    combined = clean_transactions(combined)
    return combined, loaded_files


def clean_transactions(df):
    """Parse dates, normalize amounts, handle missing values."""
    df = df.copy()

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False)

    # Ensure Amount is numeric
    if df["Amount"].dtype == object:
        df["Amount"] = df["Amount"].astype(str).str.replace(r"[$,]", "", regex=True)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    # Fill missing categories
    df["Category"] = df["Category"].fillna("Uncategorized").replace("", "Uncategorized")

    # Fill missing payees
    df["Payee"] = df["Payee"].fillna("Unknown").replace("", "Unknown")

    # Fill other string columns
    for col in ["Account", "Tags", "Memo"]:
        df[col] = df[col].fillna("")

    # Sort by date
    df = df.sort_values("Date").reset_index(drop=True)

    # Add helper columns
    df["YearMonth"] = df["Date"].dt.to_period("M")
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    df["Year"] = df["Date"].dt.year
    df["Day"] = df["Date"].dt.day

    return df
