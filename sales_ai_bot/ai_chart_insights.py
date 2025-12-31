def chart_insight(title, df):
    try:
        if "Monthly" in title and "revenue" in df.columns and "date" in df.columns:
            peak = df.loc[df["revenue"].idxmax()]
            return f"Sales peak in {peak['date'].strftime('%B %Y')}, indicating strong seasonality."
        if "Top Products" in title and "product" in df.columns and "revenue" in df.columns:
            top = df.iloc[0]
            return f"{top['product']} drives the highest revenue and should remain a priority focus."
    except Exception:
        pass
    return "This chart highlights a key performance trend worth monitoring."
