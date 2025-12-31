import pandas as pd

def detect_patterns(df, cols):
    patterns = []
    rev = cols.get("revenue")
    cust = cols.get("customer")
    region = cols.get("region")
    if rev and rev in df.columns:
        r = pd.to_numeric(df[rev], errors="coerce").fillna(0)
        if r.skew() > 2:
            patterns.append("Highly skewed revenue (few dominate)")
        if cust and cust in df.columns and r.sum() > 0:
            top10_share = (
                df.groupby(cust)[rev].sum().sort_values(ascending=False).head(10).sum()
                / float(r.sum())
            )
            if top10_share > 0.4:
                patterns.append("Revenue concentration risk")
    if region and region in df.columns:
        if df[region].nunique() > 5:
            patterns.append("Multi-region behavior")
    return patterns
