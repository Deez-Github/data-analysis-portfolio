"""Data cleaning pipeline for the retail sales dataset.

Reads the raw CSV, standardizes formats, handles missing values,
fixes data-quality issues and writes a cleaned dataset to data/processed/.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "retail_sales.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "retail_sales_clean.csv"


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw dataset."""
    return pd.read_csv(path, parse_dates=["order_date"])


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the full cleaning pipeline."""
    df = df.copy()

    # 1. Standardize text columns (fix inconsistent casing)
    for col in ["category", "region", "channel"]:
        df[col] = df[col].astype(str).str.strip().str.title()
    df["channel"] = df["channel"].replace({"Online": "Online", "In-Store": "In-Store"})

    # 2. Missing unit prices -> impute with the category median
    df["unit_price"] = df.groupby("category")["unit_price"].transform(
        lambda s: s.fillna(s.median())
    )

    # 3. Recalculate derived columns to guarantee consistency
    df["revenue"] = (df["unit_price"] * df["quantity"]).round(2)
    df["discount_amount"] = (df["revenue"] * df["discount_pct"] / 100).round(2)
    df["net_revenue"] = (df["revenue"] - df["discount_amount"]).round(2)

    # 4. Sanity checks: drop impossible rows
    df = df[df["quantity"] >= 1]
    df = df[df["unit_price"] > 0]

    # 5. Add useful time features for analysis
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["month_name"] = df["order_date"].dt.month_name()

    # 6. De-duplicate on order_id (keep first)
    df = df.drop_duplicates(subset="order_id", keep="first")

    return df.reset_index(drop=True)


def main() -> None:
    df = load_raw()
    print(f"Raw shape:      {df.shape}")
    df = clean_data(df)
    print(f"Cleaned shape:  {df.shape}")
    print(f"Missing values: {int(df.isna().sum().sum())}")
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved -> {CLEAN_PATH}")


if __name__ == "__main__":
    main()
