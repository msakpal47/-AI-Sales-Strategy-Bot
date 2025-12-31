import pandas as pd
from analysis_engine import sales_summary
from strategy_engine import generate_strategy
from upgrade.forecasting import forecast_sales
from upgrade.churn import churn_model

def detect_patterns(df, cols):
    p = {}
    rev_col = cols.get("revenue")
    cust_col = cols.get("customer")
    reg_col = cols.get("region")
    prod_col = cols.get("product")
    if rev_col and rev_col in df.columns:
        r = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
        p["revenue_skew"] = float(r.skew())
        total = float(r.sum()) if r.sum() != 0 else 0.0
        if cust_col and cust_col in df.columns and total > 0:
            top10 = df.groupby(cust_col)[rev_col].sum().sort_values(ascending=False).head(10).sum()
            p["customer_concentration"] = float(top10) / total
    if reg_col and reg_col in df.columns:
        p["region_count"] = int(df[reg_col].nunique())
    if prod_col and prod_col in df.columns:
        p["product_count"] = int(df[prod_col].nunique())
    return p

def build_segments(df, cols):
    segments = {}
    rev_col = cols.get("revenue")
    if rev_col and rev_col in df.columns:
        r = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
        q80 = r.quantile(0.8)
        q40 = r.quantile(0.4)
        segments["High Value"] = df[r > q80]
        segments["Mid Tier"] = df[(r <= q80) & (r >= q40)]
        segments["Low Value"] = df[r < q40]
    reg_col = cols.get("region")
    if reg_col and reg_col in df.columns:
        for rg in df[reg_col].dropna().unique()[:6]:
            segments[f"Region: {rg}"] = df[df[reg_col] == rg]
    prod_col = cols.get("product")
    if prod_col and prod_col in df.columns:
        for pc in df[prod_col].dropna().unique()[:6]:
            segments[f"Product: {pc}"] = df[df[prod_col] == pc]
    return segments

def analyze_segment(sdf, cols):
    s = sales_summary(sdf, cols)
    try:
        date_col = cols.get("date")
        rev_col = cols.get("revenue")
        fc = forecast_sales(sdf, date_col, rev_col, model="linear", val_months=3) if date_col and rev_col else None
    except Exception:
        fc = None
    try:
        cust_col = cols.get("customer")
        date_col = cols.get("date")
        cm = churn_model(sdf, cust_col, date_col) if cust_col and date_col else None
    except Exception:
        cm = None
    strat = generate_strategy(s)
    return {"summary": s, "forecast": fc, "churn": cm, "strategy": strat}

stakeholder_views = {
    "CEO": ["total_revenue", "growth_pct", "risk"],
    "Sales Head": ["top_products", "top_regions", "targets"],
    "Marketing": ["segments", "discount_effectiveness"],
    "Ops": ["forecast", "seasonality"]
}

def build_view(seg_data, role):
    out = {}
    if role == "CEO":
        out["total_revenue"] = seg_data["summary"].get("total_revenue", 0.0)
        cm = seg_data.get("churn")
        out["risk"] = int(len(cm["customers_at_risk"])) if cm and "customers_at_risk" in cm else 0
        out["growth_pct"] = seg_data["summary"].get("growth_pct", 0.0)
    elif role == "Sales Head":
        s = seg_data["summary"]
        out["top_products"] = list(getattr(s.get("top_products"), "index", [])[:5]) if s.get("top_products") is not None else []
        out["top_regions"] = list(getattr(s.get("top_regions"), "index", [])[:5]) if s.get("top_regions") is not None else []
    elif role == "Marketing":
        out["segments"] = "High/Mid/Low value and Region/Product slices"
        out["discount_effectiveness"] = "See price-discount effectiveness section"
    elif role == "Ops":
        fc = seg_data.get("forecast")
        out["forecast"] = fc["next_month_forecast"] if fc else None
        out["seasonality"] = seg_data["summary"].get("seasonality")
    return out

def executive_synthesis(segment_summaries):
    lines = []
    for name, data in segment_summaries.items():
        tr = data["summary"].get("total_revenue", 0.0)
        cm = data.get("churn")
        risk = int(len(cm["customers_at_risk"])) if cm and "customers_at_risk" in cm else 0
        lines.append(f"{name}: Revenue {tr:,.2f}, Risk {risk} customers at risk.")
    return lines
