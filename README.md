# Retail Sales Data Analysis

A complete, reproducible data analysis project: end-to-end pipeline from raw
(synthetic) retail transactions to cleaned data, exploratory analysis,
figures, and an automated Markdown report.

![Retail sales overview dashboard](reports/figures/overview_dashboard.png)

## Business Questions

1. Which categories and regions drive the most revenue?
2. How is revenue trending over time?
3. Do discounts increase average order value?
4. Which categories have the highest return rates?

## Project Structure

```
data-analysis-portfolio/
├── data/
│   ├── raw/                     # synthetic raw dataset (generated)
│   └── processed/               # cleaned dataset (produced by pipeline)
├── notebooks/
│   └── 01_eda.ipynb             # interactive exploratory analysis
├── reports/
│   ├── analysis_report.md       # auto-generated report
│   └── figures/                 # all charts (PNG)
├── src/
│   ├── generate_data.py         # create the synthetic raw dataset
│   ├── data_cleaning.py         # cleaning pipeline
│   ├── eda.py                   # analysis + core figures + report
│   └── visuals.py               # extra charts and overview dashboard
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Quick Start

```bash
git clone https://github.com/<your-username>/data-analysis-portfolio.git
cd data-analysis-portfolio

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Full pipeline (any step is also runnable on its own)
python src/generate_data.py     # optional — raw data is already committed
python src/data_cleaning.py
python src/eda.py
python src/visuals.py           # extra charts
```

Then open `notebooks/01_eda.ipynb` for the interactive exploration.

## Data Cleaning

The raw file (`data/raw/retail_sales.csv`, 5,000 rows) is cleaned by
`src/data_cleaning.py` into `data/processed/retail_sales_clean.csv`
(5,000 rows, 17 columns).

- **Text standardisation:** `category`, `region` and `channel` are trimmed and title-cased. This fixed inconsistent casing in `channel` ("online" vs "Online").
- **Missing values:** 40 rows had a missing `unit_price`. Each was filled with the median `unit_price` of its category.
- **Derived columns recalculated:** `revenue`, `discount_amount` and `net_revenue` are recomputed from `unit_price`, `quantity` and `discount_pct` so they stay consistent (this updated the 40 imputed rows).
- **Sanity checks:** rows with `quantity` below 1 or `unit_price` of 0 or less are dropped. None were found.
- **Duplicates:** de-duplicated on `order_id`. None were found.
- **New features:** `year`, `month`, `quarter` and `month_name` are added from `order_date`.

## Key Findings (on the generated dataset)

| Metric | Value |
|---|---|
| Total net revenue | ~$1.69M |
| Orders | 5,000 |
| Avg order value | ~$339 (median ~$232) |
| Return rate | ~8% |
| Unique customers | 1,446 |
| Top category | Electronics (~51% of revenue) |

**Revenue drivers**
- Electronics makes up about 51% of revenue from 24% of orders, with an average order value of ~$718. Books is the smallest category at about 2%.
- Online brings in about 53% of revenue and In-Store about 47%. Online leads in every region, though West is almost level.
- North is the top region (~28% of revenue) and West the lowest (~22%).

**Trends**
- Annual revenue declined: ~$587K in 2023, ~$558K in 2024 (-4.9%) and ~$548K in 2025 (-1.9%).
- There is no strong seasonality. July is the highest month on average and February the lowest, but the spread is small.
- Monthly revenue is noisy (about 11% standard deviation month to month).

**Discounts and returns**
- About 76% of orders have no discount. Average net revenue per order is ~$349 with no discount and ~$268 at 20% off, so larger discounts do **not** increase order value in this data. Because the figures are net of discount, part of that gap is mechanical.
- Return rates are fairly stable at ~8%. Home & Kitchen (9.4%) and Beauty (8.8%) are above average, and Books is lowest (5.9%).
- South (9.1%) and East (8.4%) have higher return rates than North and West (7.2%). In-Store returns (8.5%) run above Online (7.5%).

**Customers**
- Revenue is spread widely: the top 10 customers account for only about 3% of net revenue.

## Visuals

### Sales trends
| | |
|:---:|:---:|
| ![monthly_revenue_trend](reports/figures/monthly_revenue_trend.png) | ![cumulative_revenue](reports/figures/cumulative_revenue.png) |
| ![annual_revenue](reports/figures/annual_revenue.png) | ![quarterly_revenue](reports/figures/quarterly_revenue.png) |
| ![seasonality_by_month](reports/figures/seasonality_by_month.png) | ![revenue_heatmap_month_year](reports/figures/revenue_heatmap_month_year.png) |
| ![orders_by_weekday](reports/figures/orders_by_weekday.png) |  |

### Categories and products
| | |
|:---:|:---:|
| ![revenue_by_category](reports/figures/revenue_by_category.png) | ![category_revenue_share](reports/figures/category_revenue_share.png) |
| ![yearly_revenue_by_category](reports/figures/yearly_revenue_by_category.png) | ![aov_by_category](reports/figures/aov_by_category.png) |
| ![unit_price_by_category](reports/figures/unit_price_by_category.png) | ![units_per_order](reports/figures/units_per_order.png) |

### Regions and channels
| | |
|:---:|:---:|
| ![revenue_by_region](reports/figures/revenue_by_region.png) | ![revenue_by_region_channel](reports/figures/revenue_by_region_channel.png) |
| ![channel_by_category](reports/figures/channel_by_category.png) | ![category_region_heatmap](reports/figures/category_region_heatmap.png) |

### Discounts, order value and returns
| | |
|:---:|:---:|
| ![discount_impact](reports/figures/discount_impact.png) | ![discount_orders_and_aov](reports/figures/discount_orders_and_aov.png) |
| ![order_value_distribution](reports/figures/order_value_distribution.png) | ![return_rate_by_category](reports/figures/return_rate_by_category.png) |
| ![return_rate_region_channel](reports/figures/return_rate_region_channel.png) |  |

### Customers
| | |
|:---:|:---:|
| ![top_customers](reports/figures/top_customers.png) |  |

## Tech Stack

Python 3.11+ · pandas · NumPy · Matplotlib · Jupyter

## Notes

The dataset is **synthetic** (seeded RNG, 2023–2025) and generated by
`src/generate_data.py`, so every number in this repo is fully reproducible
without any external downloads or credentials.

## License

MIT — see [LICENSE](LICENSE).
