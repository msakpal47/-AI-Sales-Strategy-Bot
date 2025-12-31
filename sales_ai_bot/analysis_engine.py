import pandas as pd

def sales_summary(df, cols):
    summary = {}
    rev_col = cols.get('revenue')
    if not rev_col:
        raise ValueError("Revenue column not detected")

    df = df.copy()
    df[rev_col] = pd.to_numeric(df[rev_col], errors='coerce').fillna(0)

    summary['total_revenue'] = float(df[rev_col].sum())

    if cols.get('product'):
        top_products = (
            df.dropna(subset=[cols['product']])
            .groupby(cols['product'])[rev_col]
            .sum().sort_values(ascending=False).head(5)
        )
    else:
        top_products = pd.Series([], dtype='float64')

    if cols.get('customer'):
        top_customers = (
            df.dropna(subset=[cols['customer']])
            .groupby(cols['customer'])[rev_col]
            .sum().sort_values(ascending=False).head(5)
        )
    else:
        top_customers = pd.Series([], dtype='float64')

    if cols.get('region'):
        top_regions = (
            df.dropna(subset=[cols['region']])
            .groupby(cols['region'])[rev_col]
            .sum().sort_values(ascending=False).head(5)
        )
    else:
        top_regions = pd.Series([], dtype='float64')

    summary['top_products'] = top_products
    summary['top_customers'] = top_customers
    summary['top_regions'] = top_regions
    return summary

def _monthly(df, date_col, value_col, group_col=None):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors='coerce')
    d = d.dropna(subset=[date_col])
    if group_col:
        g = d.groupby([pd.Grouper(key=date_col, freq="M"), group_col])[value_col].sum().reset_index()
    else:
        g = d.resample("M", on=date_col)[value_col].sum().reset_index()
    return g

def product_zone_analysis(df, cols):
    rev = cols.get("revenue")
    prod = cols.get("product")
    date = cols.get("date")
    mar = cols.get("margin")
    if not rev or not prod:
        return pd.DataFrame(columns=["product", "revenue", "growth_pct", "revenue_percentile", "margin_value", "category"])
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    if mar and mar in d.columns:
        d[mar] = pd.to_numeric(d[mar], errors="coerce").fillna(0)
    by_prod = d.groupby(prod)[rev].sum().sort_values(ascending=False)
    ranks = by_prod.rank(pct=True, ascending=True)
    rev_pct = (ranks * 100).round(2)
    growth = pd.Series(0.0, index=by_prod.index)
    if date:
        m = _monthly(d, date, rev, prod)
        def grp_growth(x):
            x = x.sort_values(date)
            if len(x) < 6:
                return 0.0
            recent = x[rev].tail(3).mean()
            prior = x[rev].iloc[-6:-3].mean()
            if prior == 0:
                return 0.0
            return (recent - prior) / prior
        gr = m.groupby(prod).apply(grp_growth)
        growth = gr.reindex(by_prod.index).fillna(0.0)
    margin_series = pd.Series([], dtype="float64")
    if mar and mar in d.columns:
        margin_series = d.groupby(prod)[mar].sum().reindex(by_prod.index).fillna(0.0)
    categories = []
    for p in by_prod.index:
        hr = rev_pct.loc[p] >= 80.0
        hg = growth.loc[p] > 0.0
        mg = margin_series.loc[p] if mar and mar in d.columns else None
        if hr and hg:
            c = "Star Products"
        elif hr and not hg:
            c = "Cash Cows"
        elif not hr and hg:
            c = "Question Marks"
        else:
            c = "Dead Products"
        categories.append(c)
    out = pd.DataFrame({
        "product": by_prod.index,
        "revenue": by_prod.values,
        "growth_pct": growth.reindex(by_prod.index).values,
        "revenue_percentile": rev_pct.reindex(by_prod.index).values,
        "margin_value": margin_series.reindex(by_prod.index).values if mar and mar in d.columns else None,
        "category": categories
    })
    return out

def customer_zone_analysis(df, cols):
    rev = cols.get("revenue")
    cust = cols.get("customer")
    date = cols.get("date")
    if not rev or not cust:
        return {
            "by_customer": pd.Series([], dtype="float64"),
            "repeat_count": 0,
            "one_time_count": 0
        }
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    by_customer = d.groupby(cust)[rev].sum().sort_values(ascending=False)
    counts = d.groupby(cust).size()
    repeat_count = int((counts > 1).sum())
    one_time_count = int((counts == 1).sum())
    return {
        "by_customer": by_customer,
        "repeat_count": repeat_count,
        "one_time_count": one_time_count
    }

def top5_customer_pct(df, customer_col, revenue_col):
    d = df.copy()
    d[revenue_col] = pd.to_numeric(d[revenue_col], errors="coerce").fillna(0)
    by = d.groupby(customer_col)[revenue_col].sum().sort_values(ascending=False)
    total = float(by.sum())
    if total == 0 or len(by) < 5:
        return 0.0
    return float(by.head(5).sum() / total * 100.0)

def region_zone_analysis(df, cols):
    rev = cols.get("revenue")
    reg = cols.get("region")
    date = cols.get("date")
    if not rev or not reg:
        return {
            "by_region": pd.Series([], dtype="float64"),
            "growth": pd.Series([], dtype="float64")
        }
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    by_region = d.groupby(reg)[rev].sum().sort_values(ascending=False)
    growth = pd.Series(0.0, index=by_region.index)
    if date:
        m = _monthly(d, date, rev, reg)
        def grp_growth(x):
            x = x.sort_values(date)
            if len(x) < 6:
                return 0.0
            recent = x[rev].tail(3).mean()
            prior = x[rev].iloc[-6:-3].mean()
            if prior == 0:
                return 0.0
            return (recent - prior) / prior
        gr = m.groupby(reg).apply(grp_growth)
        growth = gr.reindex(by_region.index).fillna(0.0)
    return {
        "by_region": by_region,
        "growth": growth
    }

def product_zone_bcg(df, product_col, revenue_col, date_col):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[date_col])
    monthly = d.groupby([product_col, pd.Grouper(key=date_col, freq="M")])[revenue_col].sum().reset_index()
    gr = monthly.groupby(product_col)[revenue_col].pct_change().groupby(monthly[product_col]).mean().fillna(0)
    revenue = d.groupby(product_col)[revenue_col].sum()
    percentile = revenue.rank(pct=True)
    zones = []
    for p in revenue.index:
        high_share = percentile[p] >= 0.8
        growing = gr[p] > 0
        if high_share and growing:
            zone = "Star"
        elif high_share and not growing:
            zone = "Cash Cow"
        elif not high_share and growing:
            zone = "Question Mark"
        else:
            zone = "Dead"
        zones.append([p, float(revenue[p]), float(round(gr[p], 2)), zone])
    out = pd.DataFrame(zones, columns=["Product", "Revenue", "Growth_Rate", "Category"])
    return out

def seasonality_analysis(df, cols):
    rev = cols.get("revenue")
    date = cols.get("date")
    if not rev or not date:
        return {
            "monthly": pd.DataFrame(columns=[date, rev]),
            "forecast": 0.0,
            "forecast_accuracy": None,
            "forecast_accuracy_mape_last3": None,
            "baseline_naive_accuracy": None
        }
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    monthly = _monthly(d, date, rev)
    if len(monthly) < 2:
        return {"monthly": monthly, "forecast": 0.0, "forecast_accuracy": None, "forecast_accuracy_mape_last3": None, "baseline_naive_accuracy": None}
    monthly["month_num"] = range(len(monthly))
    X = monthly[["month_num"]].iloc[:-1]
    y = monthly[rev].iloc[:-1]
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    last_pred = float(model.predict([[monthly["month_num"].iloc[-2] + 1]])[0])
    actual_last = float(monthly[rev].iloc[-1])
    forecast_accuracy = None
    if actual_last != 0:
        forecast_accuracy = 1 - abs(actual_last - last_pred) / actual_last
    next_pred = float(model.predict([[monthly["month_num"].iloc[-1] + 1]])[0])
    mape_last3 = None
    baseline_acc = None
    if len(monthly) >= 4:
        test_idx = monthly.index[-3:]
        train = monthly.drop(test_idx)
        m2 = LinearRegression()
        m2.fit(train[["month_num"]], train[rev])
        preds = m2.predict(monthly.loc[test_idx][["month_num"]])
        actuals = monthly.loc[test_idx][rev].astype(float).values
        denom = (abs(actuals) + 1e-9)
        mape_last3 = float((abs(actuals - preds) / denom).mean())
        naive = monthly[rev].shift(1).loc[test_idx].astype(float).values
        baseline_err = abs(actuals - naive) / denom
        baseline_acc = float(1 - baseline_err.mean()) if len(baseline_err) > 0 else None
    return {"monthly": monthly, "forecast": next_pred, "forecast_accuracy": forecast_accuracy, "forecast_accuracy_mape_last3": mape_last3, "baseline_naive_accuracy": baseline_acc}

def price_discount_effectiveness(df, cols):
    rev = cols.get("revenue")
    disc = cols.get("discount")
    qty = cols.get("quantity")
    if not rev or not disc:
        return {"scatter": None, "corr": None}
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    d[disc] = pd.to_numeric(d[disc], errors="coerce").fillna(0)
    if qty and qty in d.columns:
        d[qty] = pd.to_numeric(d[qty], errors="coerce").fillna(0)
    corr = float(d[[disc, rev]].corr().iloc[0, 1])
    scatter = d[[disc, rev]].rename(columns={disc: "discount", rev: "revenue"})
    return {"scatter": scatter, "corr": corr}

def compute_kpis(df, summary, cols):
    rev = cols.get("revenue")
    prod = cols.get("product")
    cust = cols.get("customer")
    date = cols.get("date")
    total = float(summary.get("total_revenue", 0) or 0)
    top5p = float(summary.get("top_products", pd.Series([])).sum()) if prod else 0.0
    top5c_pct = top5_customer_pct(df, cust, rev) if cust and rev else 0.0
    kpis = {}
    kpis["total_revenue"] = total
    if date and rev:
        d = df.copy()
        d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
        m = _monthly(d, date, rev)
        if len(m) >= 6:
            recent = float(m[rev].tail(3).mean())
            prior = float(m[rev].iloc[-6:-3].mean())
            growth = ((recent - prior) / prior) if prior != 0 else 0.0
        else:
            growth = 0.0
        kpis["growth_pct"] = growth
    else:
        kpis["growth_pct"] = 0.0
    kpis["top5_products_pct"] = (top5p / total) if total > 0 else 0.0
    kpis["top5_customers_pct"] = (top5c_pct / 100.0) if total > 0 else 0.0
    kpis["churn_rate"] = None
    kpis["forecast_accuracy"] = None
    return kpis

def six_month_forecast(df, cols):
    rev = cols.get("revenue")
    date = cols.get("date")
    if not rev or not date:
        return pd.DataFrame(columns=["month", "forecast"])
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    monthly = _monthly(d, date, rev)
    if len(monthly) < 2:
        return pd.DataFrame(columns=["month", "forecast"])
    monthly["month_num"] = range(len(monthly))
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(monthly[["month_num"]], monthly[rev])
    start = int(monthly["month_num"].iloc[-1]) + 1
    future_nums = list(range(start, start + 6))
    preds = model.predict(pd.DataFrame({"month_num": future_nums}))
    last_date = pd.to_datetime(monthly[date].iloc[-1])
    future_months = [last_date + pd.DateOffset(months=i) for i in range(1, 7)]
    out = pd.DataFrame({"month": future_months, "forecast": preds})
    return out

def top_bottom_products(df, cols):
    rev = cols.get("revenue")
    prod = cols.get("product")
    if not rev or not prod:
        return pd.DataFrame(columns=["product","revenue"]), pd.DataFrame(columns=["product","revenue"])
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce").fillna(0)
    by = d.groupby(prod)[rev].sum().sort_values(ascending=False)
    top5 = by.head(5).reset_index().rename(columns={prod:"product", rev:"revenue"})
    bottom5 = by.tail(5).reset_index().rename(columns={prod:"product", rev:"revenue"})
    return top5, bottom5

def uplift_plan_for_bottom(bottom_df, cols):
    actions = []
    if len(bottom_df) == 0:
        return ["No bottom products found."]
    prods = bottom_df["product"].tolist()
    actions.append(f"Bundle {prods[:3]} with star products to increase visibility.")
    actions.append("Improve pricing using targeted discounts instead of flat offers.")
    actions.append("Run region-specific campaigns where demand is growing.")
    actions.append("Fix stock-outs and lead-times; ensure availability during peaks.")
    actions.append("Cross-sell with top categories on checkout and emails.")
    return actions
