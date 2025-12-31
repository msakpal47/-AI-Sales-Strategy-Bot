import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.linear_model import LinearRegression

try:
    from prophet import Prophet
    PROPHET = True
except Exception:
    PROPHET = False

def naive_forecast(series, h):
    return np.repeat(series.iloc[-1], h)

def linear_forecast(series, h):
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    model = LinearRegression()
    model.fit(X, y)
    future_X = np.arange(len(series), len(series) + h).reshape(-1, 1)
    return model.predict(future_X)

def forecast_sales(df, date_col, revenue_col, model="linear", val_months=3):
    data = df[[date_col, revenue_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col])
    data[revenue_col] = pd.to_numeric(data[revenue_col], errors="coerce")
    data = data.dropna()
    monthly = data.resample("M", on=date_col)[revenue_col].sum()
    if len(monthly) < val_months + 3:
        raise ValueError("Insufficient data for forecasting")
    train = monthly[:-val_months]
    valid = monthly[-val_months:]
    if model == "prophet" and PROPHET:
        pdf = train.reset_index().rename(columns={date_col: "ds", revenue_col: "y"})
        m = Prophet()
        m.fit(pdf)
        future = m.make_future_dataframe(periods=val_months, freq="M")
        pred = m.predict(future).tail(val_months)["yhat"].values
        next_fc = m.predict(m.make_future_dataframe(periods=1, freq="M")).tail(1)["yhat"].iloc[0]
        used_model = "PROPHET"
    else:
        pred = linear_forecast(train, val_months)
        next_fc = linear_forecast(monthly, 1)[0]
        used_model = "LINEAR"
    baseline = naive_forecast(train, val_months)
    return {
        "model": used_model,
        "validation_window": f"Last {val_months} months",
        "forecast_accuracy": round((1 - mean_absolute_percentage_error(valid, pred)) * 100, 1),
        "baseline_accuracy": round((1 - mean_absolute_percentage_error(valid, baseline)) * 100, 1),
        "rmse": round(float(np.sqrt(mean_squared_error(valid, pred))), 2),
        "next_month_forecast": round(float(next_fc), 2)
    }
