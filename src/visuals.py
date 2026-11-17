"""Additional visualizations for the retail sales dataset.

Reads the cleaned dataset and writes extra charts to reports/figures/.
Run after data_cleaning.py:  python src/visuals.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "retail_sales_clean.csv"
FIG_DIR = ROOT / "reports" / "figures"

BLUE, ORANGE, GREEN, RED, GREY = "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8C8C8C"
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
})

usd = FuncFormatter(lambda x, _: f"${x:,.0f}")
usd_k = FuncFormatter(lambda x, _: f"${x / 1e3:,.0f}K")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
    df["returned"] = df["returned"].astype(bool)
    return df


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG_DIR / name)
    plt.close()


def fig_category_share(df):
    s = df.groupby("category")["net_revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, _, autotexts = ax.pie(
        s, labels=s.index, autopct="%1.1f%%", startangle=90, pctdistance=0.78,
        colors=PALETTE, labeldistance=1.12, wedgeprops=dict(width=0.42, edgecolor="white"))
    for t, v in zip(autotexts, s.values):
        t.set_color("white")
        t.set_fontsize(9)
        if v / s.sum() < 0.05:
            t.set_text("")
    ax.set_title("Share of Net Revenue by Category")
    ax.text(0, 0, f"${s.sum() / 1e6:.2f}M\ntotal", ha="center", va="center",
            fontsize=13, fontweight="bold")
    save("category_revenue_share.png")


def fig_yearly_by_category(df):
    p = df.pivot_table(values="net_revenue", index="category",
                       columns="year", aggfunc="sum")
    p = p.loc[p.sum(axis=1).sort_values(ascending=False).index]
    ax = p.plot(kind="bar", figsize=(9, 4.5), rot=20, color=PALETTE[:3], width=0.8)
    ax.set_title("Net Revenue by Category and Year")
    ax.set_xlabel("")
    ax.set_ylabel("Net Revenue")
    ax.yaxis.set_major_formatter(usd_k)
    ax.legend(title="Year", frameon=False)
    save("yearly_revenue_by_category.png")


def fig_annual_revenue(df):
    y = df.groupby("year")["net_revenue"].sum()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(y.index.astype(str), y.values, color=BLUE, width=0.55)
    for i, v in enumerate(y.values):
        change = "" if i == 0 else f"\n({(v / y.values[i - 1] - 1) * 100:+.1f}% YoY)"
        ax.text(i, v, f"${v / 1e3:,.0f}K{change}", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, y.max() * 1.2)
    ax.yaxis.set_major_formatter(usd_k)
    ax.set_title("Annual Net Revenue")
    save("annual_revenue.png")


def fig_quarterly(df):
    q = df.groupby(["year", "quarter"])["net_revenue"].sum()
    labels = [f"{y} Q{k}" for y, k in q.index]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = [PALETTE[int(y) - 2023] for y, _ in q.index]
    ax.bar(labels, q.values, color=colors)
    ax.set_title("Quarterly Net Revenue")
    ax.yaxis.set_major_formatter(usd_k)
    plt.xticks(rotation=45, ha="right")
    save("quarterly_revenue.png")


def fig_seasonality(df):
    m = df.groupby(["year", "month"])["net_revenue"].sum().groupby("month").mean()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = [ORANGE if v == m.max() else BLUE for v in m.values]
    ax.bar(MONTHS, m.values, color=colors)
    ax.axhline(m.mean(), color=GREY, ls="--", lw=1, label="Average month")
    ax.set_title("Average Net Revenue by Calendar Month (2023-2025)")
    ax.yaxis.set_major_formatter(usd_k)
    ax.legend(frameon=False)
    save("seasonality_by_month.png")


def fig_month_year_heatmap(df):
    h = df.pivot_table(values="net_revenue", index="year", columns="month", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(11, 3.6))
    im = ax.imshow(h.values / 1e3, cmap="Blues", aspect="auto")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTHS)
    ax.set_yticks(range(len(h)))
    ax.set_yticklabels(h.index)
    for i in range(h.shape[0]):
        for j in range(h.shape[1]):
            v = h.values[i, j] / 1e3
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9,
                    color="white" if v > np.nanmax(h.values) / 1e3 * 0.6 else "black")
    ax.set_title("Monthly Net Revenue Heatmap ($K)")
    ax.spines[:].set_visible(False)
    fig.colorbar(im, ax=ax, pad=0.01)
    save("revenue_heatmap_month_year.png")


def fig_cumulative(df):
    d = df.set_index("order_date")["net_revenue"].sort_index().resample("D").sum().cumsum()
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(d.index, d.values, color=BLUE, lw=2)
    ax.fill_between(d.index, d.values, color=BLUE, alpha=0.12)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x / 1e6:.1f}M"))
    ax.set_title("Cumulative Net Revenue")
    save("cumulative_revenue.png")


def fig_region(df):
    r = df.groupby("region")["net_revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(r.index, r.values, color=BLUE, width=0.6)
    for i, v in enumerate(r.values):
        ax.text(i, v, f"${v / 1e3:,.0f}K\n({v / r.sum() * 100:.1f}%)",
                ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, r.max() * 1.2)
    ax.yaxis.set_major_formatter(usd_k)
    ax.set_title("Net Revenue by Region")
    save("revenue_by_region.png")


def fig_channel_category(df):
    p = df.pivot_table(values="net_revenue", index="category",
                       columns="channel", aggfunc="sum")
    p = p.loc[p.sum(axis=1).sort_values(ascending=False).index]
    ax = p.plot(kind="bar", figsize=(9, 4.5), rot=20, color=[GREEN, BLUE], width=0.75)
    ax.set_title("Net Revenue by Category and Channel")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(usd_k)
    ax.legend(title="Channel", frameon=False)
    save("channel_by_category.png")


def fig_category_region_heatmap(df):
    h = df.pivot_table(values="net_revenue", index="category",
                       columns="region", aggfunc="sum")
    h = h.loc[h.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    im = ax.imshow(h.values / 1e3, cmap="Blues", aspect="auto")
    ax.set_xticks(range(h.shape[1]))
    ax.set_xticklabels(h.columns)
    ax.set_yticks(range(h.shape[0]))
    ax.set_yticklabels(h.index)
    for i in range(h.shape[0]):
        for j in range(h.shape[1]):
            v = h.values[i, j] / 1e3
            ax.text(j, i, f"${v:,.0f}K", ha="center", va="center", fontsize=9,
                    color="white" if v > h.values.max() / 1e3 * 0.55 else "black")
    ax.set_title("Net Revenue: Category x Region")
    ax.spines[:].set_visible(False)
    save("category_region_heatmap.png")


def fig_aov_category(df):
    a = df.groupby("category")["net_revenue"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(a.index, a.values, color=BLUE)
    for i, v in enumerate(a.values):
        ax.text(v, i, f" ${v:,.0f}", va="center", fontsize=9)
    ax.axvline(df["net_revenue"].mean(), color=ORANGE, ls="--", lw=1.2,
               label=f"Overall avg (${df['net_revenue'].mean():,.0f})")
    ax.set_xlim(0, a.max() * 1.15)
    ax.set_title("Average Order Value by Category")
    ax.legend(frameon=False, loc="lower right")
    save("aov_by_category.png")


def fig_order_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df["net_revenue"], bins=np.logspace(0.5, np.log10(df["net_revenue"].max()), 40),
            color=BLUE, edgecolor="white")
    ax.set_xscale("log")
    ax.axvline(df["net_revenue"].median(), color=ORANGE, ls="--",
               label=f"Median ${df['net_revenue'].median():,.0f}")
    ax.axvline(df["net_revenue"].mean(), color=RED, ls="--",
               label=f"Mean ${df['net_revenue'].mean():,.0f}")
    ax.set_xlabel("Net revenue per order ($, log scale)")
    ax.set_ylabel("Orders")
    ax.set_title("Distribution of Order Value")
    ax.legend(frameon=False)
    save("order_value_distribution.png")


def fig_price_box(df):
    order = df.groupby("category")["unit_price"].median().sort_values(ascending=False).index
    data = [df.loc[df["category"] == c, "unit_price"] for c in order]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bp = ax.boxplot(data, tick_labels=order, patch_artist=True, showfliers=False)
    for patch in bp["boxes"]:
        patch.set_facecolor(BLUE)
        patch.set_alpha(0.65)
    for med in bp["medians"]:
        med.set_color(ORANGE)
        med.set_linewidth(2)
    ax.set_ylabel("Unit price ($)")
    ax.set_title("Unit Price Distribution by Category")
    plt.xticks(rotation=20)
    save("unit_price_by_category.png")


def fig_quantity(df):
    q = df.groupby("category")["quantity"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(q.index, q.values, color=GREEN)
    for i, v in enumerate(q.values):
        ax.text(v, i, f" {v:.2f}", va="center", fontsize=9)
    ax.set_xlim(0, q.max() * 1.15)
    ax.set_title("Average Units per Order by Category")
    save("units_per_order.png")


def fig_discount(df):
    g = df.groupby("discount_pct").agg(orders=("order_id", "count"),
                                       avg=("net_revenue", "mean"))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
    axs[0].bar(g.index.astype(str), g["orders"], color=BLUE)
    for i, v in enumerate(g["orders"]):
        axs[0].text(i, v, f"{v:,}\n({v / g['orders'].sum() * 100:.0f}%)",
                    ha="center", va="bottom", fontsize=9)
    axs[0].set_ylim(0, g["orders"].max() * 1.18)
    axs[0].set_title("Orders by Discount Level")
    axs[0].set_xlabel("Discount (%)")
    axs[1].plot(g.index.astype(str), g["avg"], marker="o", color=ORANGE, lw=2.5)
    for i, v in enumerate(g["avg"]):
        axs[1].text(i, v + 6, f"${v:,.0f}", ha="center", fontsize=9)
    axs[1].set_ylim(0, g["avg"].max() * 1.2)
    axs[1].set_title("Average Order Value by Discount Level")
    axs[1].set_xlabel("Discount (%)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "discount_orders_and_aov.png")
    plt.close()


def fig_return_region_channel(df):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, col, color in zip(axs, ["region", "channel"], [RED, ORANGE]):
        r = df.groupby(col)["returned"].mean().mul(100)
        ax.bar(r.index, r.values, color=color, width=0.55)
        for i, v in enumerate(r.values):
            ax.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
        ax.axhline(df["returned"].mean() * 100, color=GREY, ls="--", lw=1)
        ax.set_ylim(0, max(r.max() * 1.3, 10))
        ax.set_title(f"Return Rate by {col.title()} (%)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "return_rate_region_channel.png")
    plt.close()


def fig_top_customers(df):
    t = df.groupby("customer_id")["net_revenue"].sum().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(t.index.astype(str), t.values, color=BLUE)
    for i, v in enumerate(t.values):
        ax.text(v, i, f" ${v:,.0f}", va="center", fontsize=9)
    ax.set_xlim(0, t.max() * 1.15)
    ax.set_ylabel("Customer ID")
    ax.set_title("Top 10 Customers by Net Revenue")
    save("top_customers.png")


def fig_weekday(df):
    d = df.groupby(df["order_date"].dt.day_name())["order_id"].count()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    d = d.reindex(order)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar([x[:3] for x in order], d.values, color=BLUE)
    ax.axhline(d.mean(), color=GREY, ls="--", lw=1)
    ax.set_title("Orders by Day of Week")
    ax.set_ylabel("Orders")
    save("orders_by_weekday.png")


def fig_overview(df):
    """One-page summary dashboard."""
    fig = plt.figure(figsize=(14, 8.5))
    gs = fig.add_gridspec(3, 4, height_ratios=[0.55, 1.6, 1.6], hspace=0.5, wspace=0.35)
    fig.suptitle("Retail Sales Overview (2023-2025)", fontsize=18, fontweight="bold", y=0.98)

    kpis = [("Net Revenue", f"${df['net_revenue'].sum() / 1e6:.2f}M"),
            ("Orders", f"{len(df):,}"),
            ("Avg Order Value", f"${df['net_revenue'].mean():,.0f}"),
            ("Return Rate", f"{df['returned'].mean() * 100:.1f}%")]
    for i, (label, value) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i])
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                   facecolor="#EEF2F8", edgecolor=BLUE, lw=1.5))
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=20,
                fontweight="bold", color=BLUE, transform=ax.transAxes)
        ax.text(0.5, 0.22, label, ha="center", va="center", fontsize=11,
                color="#444", transform=ax.transAxes)

    ax = fig.add_subplot(gs[1, :2])
    m = df.set_index("order_date")["net_revenue"].resample("ME").sum()
    ax.plot(m.index, m.values, color=BLUE, lw=2)
    ax.plot(m.index, m.rolling(3).mean(), color=ORANGE, lw=2, ls="--")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(usd_k)
    ax.set_title("Monthly Net Revenue")

    ax = fig.add_subplot(gs[1, 2:])
    c = df.groupby("category")["net_revenue"].sum().sort_values()
    ax.barh(c.index, c.values, color=BLUE)
    ax.xaxis.set_major_formatter(usd_k)
    ax.set_title("Net Revenue by Category")

    ax = fig.add_subplot(gs[2, :2])
    p = df.pivot_table(values="net_revenue", index="region",
                       columns="channel", aggfunc="sum")
    p.plot(kind="bar", ax=ax, rot=0, color=[GREEN, BLUE], width=0.7)
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(usd_k)
    ax.legend(frameon=False, title="")
    ax.set_title("Revenue by Region and Channel")

    ax = fig.add_subplot(gs[2, 2:])
    y = df.groupby("year")["net_revenue"].sum()
    ax.bar(y.index.astype(str), y.values, color=BLUE, width=0.55)
    ax.yaxis.set_major_formatter(usd_k)
    ax.set_title("Annual Net Revenue")
    plt.savefig(FIG_DIR / "overview_dashboard.png", bbox_inches="tight")
    plt.close()


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    for fn in [fig_overview, fig_category_share, fig_annual_revenue,
               fig_yearly_by_category, fig_quarterly, fig_seasonality,
               fig_month_year_heatmap, fig_cumulative, fig_region,
               fig_channel_category, fig_category_region_heatmap, fig_aov_category,
               fig_order_distribution, fig_price_box, fig_quantity, fig_discount,
               fig_return_region_channel, fig_top_customers, fig_weekday]:
        fn(df)
    print(f"Extra figures saved -> {FIG_DIR}")


if __name__ == "__main__":
    main()
