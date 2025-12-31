from analysis_engine import sales_summary
from upgrade.forecasting import forecast_sales
from upgrade.churn import churn_model
from strategy_engine import generate_strategy

def run_segments(segments, cols):
    results = {}
    for name, sdf in segments.items():
        if len(sdf) < 20:
            continue
        summary = sales_summary(sdf, cols)
        date_col = cols.get("date")
        rev_col = cols.get("revenue")
        cust_col = cols.get("customer")
        try:
            forecast = forecast_sales(sdf, date_col, rev_col, model="linear", val_months=3) if date_col and rev_col else None
        except Exception:
            forecast = None
        try:
            churn = churn_model(sdf, cust_col, date_col) if cust_col and date_col else None
        except Exception:
            churn = None
        results[name] = {
            "summary": summary,
            "forecast": forecast,
            "churn": churn,
            "strategy": generate_strategy(summary)
        }
    return results
