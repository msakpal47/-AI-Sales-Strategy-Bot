def data_health(df, cols):
    issues = []
    if df is None or len(df) == 0:
        issues.append("Dataset is empty")
        return issues
    rev = cols.get("revenue")
    cust = cols.get("customer")
    if rev and rev in df.columns:
        if df[rev].isna().mean() > 0.1:
            issues.append("Revenue column has >10% missing values")
    if cust and cust in df.columns:
        if df[cust].nunique() < 5:
            issues.append("Very few unique customers")
    return issues
