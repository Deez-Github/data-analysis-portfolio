"""Generate the synthetic raw retail sales dataset (data/raw/retail_sales.csv).

The dataset is synthetic and generated with a fixed seed for full
reproducibility. Run:  python src/generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "retail_sales.csv"


def main() -> None:
    rng = np.random.default_rng(42)
    n = 5000
    start, end = pd.Timestamp("2023-01-01").value, pd.Timestamp("2025-12-31").value
    dates = pd.to_datetime(rng.integers(start, end, n)).normalize()

    categories = ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Sports", "Books"]
    regions = ["North", "South", "East", "West"]
    channels = ["Online", "In-Store"]

    df = pd.DataFrame({
        "order_id": [f"ORD-{i:06d}" for i in range(1, n + 1)],
        "order_date": dates,
        "category": rng.choice(categories, n, p=[0.24, 0.22, 0.18, 0.14, 0.12, 0.10]),
        "region": rng.choice(regions, n, p=[0.28, 0.26, 0.24, 0.22]),
        "channel": rng.choice(channels, n, p=[0.55, 0.45]),
        "customer_id": rng.integers(1000, 2500, n),
    })

    base_price = {"Electronics": 320, "Clothing": 65, "Home & Kitchen": 95,
                  "Beauty": 38, "Sports": 85, "Books": 22}
    df["unit_price"] = df["category"].map(base_price) * rng.lognormal(0, 0.35, n)
    qty_lambda = df["category"].map(lambda c: 1.1 if c == "Electronics" else 2.2)
    df["quantity"] = rng.poisson(qty_lambda) + 1
    df["revenue"] = (df["unit_price"] * df["quantity"]).round(2)
    df["discount_pct"] = rng.choice([0, 0, 0, 5, 10, 15, 20], n,
                                    p=[0.5, 0.15, 0.1, 0.1, 0.07, 0.05, 0.03])
    df["discount_amount"] = (df["revenue"] * df["discount_pct"] / 100).round(2)
    df["net_revenue"] = df["revenue"] - df["discount_amount"]
    df["returned"] = rng.random(n) < 0.08

    # Intentional messiness for the cleaning step to handle
    df.loc[rng.choice(df.index, 40, replace=False), "unit_price"] = np.nan
    df.loc[rng.choice(df.index, 15, replace=False), "channel"] = "online"

    df = df.sort_values("order_date").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {OUT} ({df.shape[0]:,} rows, {df.shape[1]} cols)")


if __name__ == "__main__":
    main()
