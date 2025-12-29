import io
import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sales_ai_bot.profiler import detect_columns
from sales_ai_bot.analysis_engine import sales_summary, compute_kpis, seasonality_analysis, product_zone_analysis, customer_zone_analysis, region_zone_analysis, six_month_forecast, top_bottom_products, uplift_plan_for_bottom
from sales_ai_bot.charts import create_charts
from sales_ai_bot.pdf_report import build_executive_report
from sales_ai_bot.reports import build_sales_report

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _load_df(file: UploadFile) -> pd.DataFrame:
    name = file.filename or "upload.csv"
    content = file.file.read()
    buf = io.BytesIO(content)
    if name.lower().endswith(".xlsx") or name.lower().endswith(".xls"):
        df = pd.read_excel(buf)
    else:
        df = pd.read_csv(buf)
    return df

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    try:
        df = _load_df(file)
        cols = detect_columns(df)
        summary = sales_summary(df, cols)
        kpis = compute_kpis(df, summary, cols)
        sa = seasonality_analysis(df, cols)
        pz = product_zone_analysis(df, cols)
        cz = customer_zone_analysis(df, cols)
        rz = region_zone_analysis(df, cols)
        smf = six_month_forecast(df, cols)
        t5, b5 = top_bottom_products(df, cols)
        uplift = uplift_plan_for_bottom(b5, cols)
        return JSONResponse({
            "kpis": kpis,
            "seasonality": {"forecast": sa.get("forecast"), "accuracy": sa.get("forecast_accuracy")},
            "top_products": summary.get("top_products").to_dict(),
            "top_customers": summary.get("top_customers").to_dict(),
            "top_regions": summary.get("top_regions").to_dict(),
            "product_zone": pz.to_dict(orient="records"),
            "customer_analysis": {
                "repeat_count": cz.get("repeat_count"),
                "one_time_count": cz.get("one_time_count"),
            },
            "region_analysis": {
                "growth": rz.get("growth").to_dict(),
            },
            "six_month_forecast": smf.to_dict(orient="records"),
            "bottom5_uplift": uplift,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.post("/reports/executive")
def executive_report(
    file: UploadFile = File(...),
    brand: str = Form(None)
):
    df = _load_df(file)
    cols = detect_columns(df)
    summary = sales_summary(df, cols)
    sa = seasonality_analysis(df, cols)
    pz = product_zone_analysis(df, cols)
    cz = customer_zone_analysis(df, cols)
    rz = region_zone_analysis(df, cols)
    monthly_df = sa["monthly"]
    if len(monthly_df) > 0 and cols.get("date") and cols.get("revenue"):
        monthly_for_chart = monthly_df.rename(columns={cols["date"]: "date", cols["revenue"]: "revenue"})
    else:
        monthly_for_chart = pd.DataFrame(columns=["date", "revenue"])
    product_for_chart = pz[["product", "revenue"]] if cols.get("product") else pd.DataFrame(columns=["product", "revenue"])
    charts = create_charts(monthly_for_chart, product_for_chart)
    risk = "High"
    findings = []
    if summary.get("top_products") is not None and len(summary["top_products"]) > 0:
        findings.append("Revenue concentrated in few products.")
    data = {
        "revenue": float(summary.get("total_revenue", 0)),
        "growth": float(compute_kpis(df, summary, cols).get("growth_pct", 0.0)),
        "forecast": float(sa.get("forecast", 0.0)),
        "risk": risk,
        "findings": findings,
        "sales_comment": "Use forecast to plan inventory, manpower, and promotions.",
        "product_actions": ["Focus on star products", "Optimize cash cows", "Improve pricing for question marks", "Bundle dead products"],
        "customer_region_risk": ["Investigate low-performing regions for price/logistics/competition"],
        "strategies": ["Protect high-value customers", "Win-back inactive customers", "Targeted pricing by region"]
    }
    out_path = os.path.join("sales_ai_bot", "pdf", "executive_api.pdf")
    build_executive_report(data, charts, out_path, brand=brand)
    with open(out_path, "rb") as f:
        b = f.read()
    return StreamingResponse(io.BytesIO(b), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=executive_report.pdf"})

@app.post("/reports/strategy")
def strategy_report(
    file: UploadFile = File(...),
    brand: str = Form(None)
):
    df = _load_df(file)
    cols = detect_columns(df)
    summary = sales_summary(df, cols)
    summary["df_source"] = df
    summary["cols_source"] = cols
    sa = seasonality_analysis(df, cols)
    pz = product_zone_analysis(df, cols) if cols.get("product") else None
    cz = customer_zone_analysis(df, cols)
    rz = region_zone_analysis(df, cols)
    kpis = compute_kpis(df, summary, cols)
    charts = None
    out_path = build_sales_report(summary, ["Protect high-value customers", "Win-back inactive customers"], pz, cz, rz, sa, kpis, charts=charts, brand=brand)
    with open(out_path, "rb") as f:
        b = f.read()
    return StreamingResponse(io.BytesIO(b), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=sales_strategy.pdf"})

@app.get("/favicon.ico")
def favicon():
    return JSONResponse({}, status_code=204)
