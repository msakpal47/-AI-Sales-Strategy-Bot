import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def create_charts(monthly_df, product_df, out_dir="reports/charts"):
    os.makedirs(out_dir, exist_ok=True)
    p1 = os.path.join(out_dir, "monthly_trend.png")
    plt.figure(figsize=(8, 4))
    plt.plot(monthly_df["date"], monthly_df["revenue"], marker="o")
    plt.title("Monthly Sales Trend")
    plt.tight_layout()
    plt.savefig(p1)
    plt.close()
    p2 = os.path.join(out_dir, "top_products.png")
    plt.figure(figsize=(8, 4))
    plt.bar(product_df["product"], product_df["revenue"])
    plt.title("Top Products by Revenue")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(p2)
    plt.close()
    return {
        "Monthly Sales Trend": {"path": p1, "df": monthly_df},
        "Top Products by Revenue": {"path": p2, "df": product_df}
    }
