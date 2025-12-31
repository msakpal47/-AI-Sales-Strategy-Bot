import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score

def churn_risk(df, customer_col, date_col):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    last_purchase = df.groupby(customer_col)[date_col].max().reset_index()
    last_purchase["days_inactive"] = (
        pd.Timestamp.today() - pd.to_datetime(last_purchase[date_col])
    ).dt.days
    risky = last_purchase[last_purchase["days_inactive"] > 60]
    return risky

def churn_proba(df, customer_col, date_col):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors='coerce')
    d = d.dropna(subset=[date_col])
    lp = d.groupby(customer_col)[date_col].max().reset_index()
    lp["days_inactive"] = (pd.Timestamp.today() - pd.to_datetime(lp[date_col])).dt.days
    x = (lp["days_inactive"] - 60) / 30.0
    p = 1.0 / (1.0 + np.exp(-x))
    out = lp[[customer_col, "days_inactive"]].copy()
    out["p_churn"] = p
    return out

def churn_model(df, customer_col, date_col):
    data = df[[customer_col, date_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    data = data.dropna(subset=[date_col])
    last_date = data[date_col].max()
    churn_df = data.groupby(customer_col)[date_col].max().reset_index()
    churn_df["recency_days"] = (last_date - churn_df[date_col]).dt.days
    churn_df["churn"] = (churn_df["recency_days"] > 90).astype(int)
    X = churn_df[["recency_days"]]
    y = churn_df["churn"]
    model = LogisticRegression()
    model.fit(X, y)
    churn_df["p_churn"] = model.predict_proba(X)[:, 1]
    threshold = 0.7
    churn_df["flagged"] = churn_df["p_churn"] > threshold
    precision = precision_score(y, churn_df["flagged"])
    recall = recall_score(y, churn_df["flagged"])
    return {
        "threshold": threshold,
        "customers_at_risk": churn_df[churn_df["flagged"]],
        "precision": round(float(precision), 2),
        "recall": round(float(recall), 2)
    }
