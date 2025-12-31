import pandas as pd

def auto_segment(df, cols):
    rev = cols.get("revenue")
    if not rev or rev not in df.columns:
        return {}
    r = pd.to_numeric(df[rev], errors="coerce").fillna(0)
    q80 = r.quantile(0.8)
    q40 = r.quantile(0.4)
    return {
        "High Value": df[r >= q80],
        "Mid Value": df[(r < q80) & (r >= q40)],
        "Low Value": df[r < q40],
    }
