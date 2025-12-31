import os
import re
from datetime import datetime
from fpdf import FPDF
import pandas as pd

def _list_text(items):
    if not items:
        return "-"
    if isinstance(items, list):
        return ", ".join([str(x) for x in items[:10]])
    return str(items)

def _safe_text(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace("₹", "INR ").replace("–", "-").replace("—", "-").replace("•", "-")
    s = s.replace("“", "\"").replace("”", "\"").replace("’", "'")
    s = s.replace("↑", " up ").replace("↓", " down ").replace("⚠️", " WARNING ").replace("⭐", "*")
    s = re.sub(r"[^\x20-\x7E\n]", "", s)
    return s

def build_sales_report(summary, strategies, product_zone_df, customer_analysis, region_analysis, seasonality, kpis, output_dir="sales_ai_bot/pdf", file_name=None, charts=None, brand=None, logo_path=None, forecast_info=None, churn_info=None):
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = file_name or f"sales_strategy_{ts}.pdf"
    path = os.path.join(output_dir, name)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _safe_text(brand or "AI Sales Strategy Report"), ln=True, align="C")
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=pdf.w - 60, y=20, w=40)
        except Exception:
            pass
    pdf.ln(18)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, _safe_text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True)
    pdf.ln(2)

    epw = pdf.w - pdf.l_margin - pdf.r_margin
    def write_lines(lines, size=12):
        pdf.set_font("Helvetica", "", size)
        if isinstance(lines, str):
            lines = [lines]
        for line in lines:
            t = _safe_text(line)
            # wrap manually for very long tokens
            while len(t) > 0:
                chunk = t[:120]
                pdf.multi_cell(epw, 8, chunk)
                t = t[120:]

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Executive KPIs (Clean)"), ln=True)
    write_lines([f"Total Revenue: {kpis.get('total_revenue', 0):,.2f}"])
    growth_pct = kpis.get('growth_pct', 0.0)
    sign = "+" if growth_pct >= 0 else "-"
    write_lines([f"Growth: {sign}{abs(growth_pct)*100:,.1f}%"])
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _safe_text("Revenue Concentration"), ln=True)
    pdf.set_font("Helvetica", "", 12)
    write_lines([f"• Top 5 Products: {kpis.get('top5_products_pct', 0.0)*100:,.1f}%"])
    t5c = kpis.get('top5_customers_pct', 0.0)
    if t5c and t5c > 0:
        write_lines([f"• Top 5 Customers: {t5c*100:,.1f}%"])
    else:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _safe_text("⚠️ Data Quality Warning"), ln=True)
        pdf.set_font("Helvetica", "", 12)
        write_lines([
            "Top 5 Customers % could not be computed reliably.",
            "Possible causes:",
            "• Incorrect customer ID mapping",
            "• Non-numeric revenue column",
            "• Sparse transactions per customer",
            "Action Required: Verify customer and revenue columns before production use."
        ])
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Forecast Methodology"), ln=True)
    if forecast_info:
        write_lines([
            f"• Model: {forecast_info.get('model')}",
            f"• Validation Window: {forecast_info.get('validation_window')}",
            "• Accuracy Metric: MAPE",
            f"• Forecast Accuracy: {forecast_info.get('forecast_accuracy')}%",
            f"• Baseline (Naive): {forecast_info.get('baseline_accuracy')}%",
            f"• RMSE: {forecast_info.get('rmse')}"
        ])
    else:
        write_lines("Unavailable due to missing date or revenue columns.")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Churn Risk Model"), ln=True)
    write_lines([
        "• Algorithm: Logistic Regression",
        "• Feature: Recency (days since last purchase)",
        "• Threshold: P(churn) > 0.70"
    ])
    if churn_info:
        write_lines([
            f"Results",
            f"• Customers at Risk: {int(churn_info.get('count', 0))}",
            f"• Precision: {churn_info.get('precision', 0.0)}",
            f"• Recall: {churn_info.get('recall', 0.0)}"
        ])
    else:
        write_lines("Unavailable due to missing customer or date columns.")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Product Zone Classification (BCG Logic)"), ln=True)
    pdf.set_font("Helvetica", "", 12)
    write_lines([
        "Rules Used:",
        "• Revenue percentile ≥ 80% → High market share",
        "• Growth rate > 0 → Growing",
        "• Margin proxy used if available"
    ])
    # Try to compute BCG classification if source data is available
    bcg_rows = []
    try:
        df_src = summary.get("df_source")
        cols_src = summary.get("cols_source", {})
        prod = cols_src.get("product")
        rev = cols_src.get("revenue")
        date = cols_src.get("date")
        if isinstance(df_src, pd.DataFrame) and prod and rev and date:
            from analysis_engine import product_zone_bcg
            bcg = product_zone_bcg(df_src, prod, rev, date)
            if bcg is not None and len(bcg) > 0:
                bcg_rows = bcg.values.tolist()
    except Exception:
        bcg_rows = []
    if len(bcg_rows) > 0:
        classes = []
        for row in bcg_rows:
            p = row[0]
            cat = row[3]
            if cat == "Star":
                desc = "High Share + Growth"
            elif cat == "Cash Cow":
                desc = "High Share + Stable"
            elif cat == "Question Mark":
                desc = "Low Share + Growth"
            else:
                desc = "Low Share + Decline"
            classes.append(f"• {cat}: {p} ({desc})")
        write_lines(["Classification:"] + classes)
    else:
        write_lines("Classification unavailable due to insufficient product/date columns.")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Product Zone Analysis"), ln=True)
    if product_zone_df is not None and len(product_zone_df) > 0:
        stars = product_zone_df[product_zone_df["category"] == "Star Products"]["product"].tolist()
        cows = product_zone_df[product_zone_df["category"] == "Cash Cows"]["product"].tolist()
        qmarks = product_zone_df[product_zone_df["category"] == "Question Marks"]["product"].tolist()
        deads = product_zone_df[product_zone_df["category"] == "Dead Products"]["product"].tolist()
        write_lines([
            f"Star Products: {_list_text(stars)}",
            f"Cash Cows: {_list_text(cows)}",
            f"Question Marks: {_list_text(qmarks)}",
            f"Dead Products: {_list_text(deads)}",
        ])
    else:
        write_lines("Insufficient product data.")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Customer Zone Analysis"), ln=True)
    by_customer = customer_analysis.get("by_customer")
    repeat_count = customer_analysis.get("repeat_count", 0)
    one_time_count = customer_analysis.get("one_time_count", 0)
    top_customers = []
    if by_customer is not None and len(by_customer) > 0:
        top_customers = list(by_customer.head(5).index)
    write_lines([
        f"Top Customers: {_list_text(top_customers)}",
        f"Repeat Buyers: {repeat_count}",
        f"One-time Buyers: {one_time_count}",
    ])
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Region / Market Zone Analysis"), ln=True)
    by_region = region_analysis.get("by_region")
    top_regions = []
    if by_region is not None and len(by_region) > 0:
        top_regions = list(by_region.head(5).index)
    write_lines(f"Top Regions: {_list_text(top_regions)}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Time & Seasonality"), ln=True)
    forecast_val = seasonality.get("forecast", 0.0) if seasonality else 0.0
    acc = seasonality.get("forecast_accuracy") if seasonality else None
    write_lines(f"Next Month Forecast: {forecast_val:,.2f}")
    if acc is not None:
        write_lines(f"Forecast Accuracy: {acc*100:,.1f}%")
    pdf.ln(3)

    if charts:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, _safe_text("Sales Visual Insights"), ln=True)
        if charts.get("monthly") and os.path.exists(charts["monthly"]):
            pdf.image(charts["monthly"], x=15, w=pdf.w - 30)
            pdf.ln(5)
        if charts.get("product") and os.path.exists(charts["product"]):
            pdf.image(charts["product"], x=15, w=pdf.w - 30)
            pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Strategies"), ln=True)
    for s in strategies or []:
        write_lines(f"- {s}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Improvement Areas"), ln=True)
    imp = []
    if product_zone_df is not None and len(product_zone_df) > 0:
        if len(product_zone_df[product_zone_df["category"] == "Dead Products"]) > 0:
            imp.append("Remove or bundle dead inventory.")
        if len(product_zone_df[product_zone_df["category"] == "Question Marks"]) > 0:
            imp.append("Improve pricing or promotion for high-growth low-revenue products.")
    if by_customer is not None and len(by_customer) > 0:
        imp.append("Reduce dependency on a few major buyers.")
    for t in imp:
        write_lines(f"- {t}")
    if not imp:
        write_lines("No critical improvement areas identified.")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Outcome-led Promise"), ln=True)
    write_lines([
        "Identify which products to push",
        "Where sales are leaking",
        "Which customers to retain",
        "What to do next (clear actions)"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Proof You Need"), ln=True)
    write_lines([
        "1 pilot case study (before/after)",
        "2 screenshots (Exec view + Product zone)",
        "3 quantified wins (INR up, % down churn, up forecast)"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Business Analytics Summary"), ln=True)
    write_lines([
        f"Total revenue: {kpis.get('total_revenue', 0):,.2f}",
        f"Growth trend: {kpis.get('growth_pct', 0.0)*100:,.1f}%",
        f"Product concentration (top 5): {kpis.get('top5_products_pct', 0.0)*100:,.1f}%",
        f"Customer concentration (top 5): {kpis.get('top5_customers_pct', 0.0)*100:,.1f}%"
    ])
    tr = summary.get("top_regions")
    if tr is not None and len(tr) > 0:
        write_lines(f"Top regions: {_list_text(list(tr.index))}")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Future Prediction"), ln=True)
    fv = seasonality.get("forecast", 0.0) if seasonality else 0.0
    acc = seasonality.get("forecast_accuracy") if seasonality else None
    write_lines([f"Next month forecast: {fv:,.2f}"])
    if acc is not None:
        write_lines([f"Forecast accuracy: {acc*100:,.1f}%"])
    gt = kpis.get("growth_pct", 0.0)
    if gt > 0:
        write_lines("Trend indicates growth; prepare inventory and marketing.")
    elif gt < 0:
        write_lines("Trend indicates decline; adjust pricing and promotions.")
    else:
        write_lines("Stable trend; maintain balanced operations.")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Market Strategy"), ln=True)
    gr_series = region_analysis.get("growth") if region_analysis else None
    if gr_series is not None and len(gr_series) > 0:
        pos = [r for r, v in gr_series.items() if v > 0]
        neg = [r for r, v in gr_series.items() if v < 0]
        if len(pos) > 0:
            write_lines(f"High-growth regions: {_list_text(pos)}")
        if len(neg) > 0:
            write_lines(f"Underperforming regions: {_list_text(neg)}")
    write_lines([
        "Increase sales effort in high-growth regions.",
        "Investigate price, logistics, and competition in weak markets.",
        "Deploy region-specific offers and bundles."
    ])
    if summary and "top_products" in summary and len(summary["top_products"]) > 0:
        write_lines(f"Top products: {_list_text(list(summary['top_products'].index))}")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Six-Month Forecast"), ln=True)
    try:
        from analysis_engine import six_month_forecast, top_bottom_products, uplift_plan_for_bottom
        smf = six_month_forecast(summary.get("df_source") if isinstance(summary.get("df_source"), pd.DataFrame) else pd.DataFrame(), summary.get("cols_source", {}))
    except Exception:
        smf = None
    if smf is not None and len(smf) > 0:
        for _, row in smf.iterrows():
            write_lines(f"{row['month'].strftime('%b %Y')}: {float(row['forecast']):,.2f}")
    else:
        write_lines("Unavailable due to insufficient data.")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Bottom-5 Uplift Plan"), ln=True)
    try:
        from analysis_engine import top_bottom_products, uplift_plan_for_bottom
        if isinstance(summary.get("df_source"), pd.DataFrame):
            t5, b5 = top_bottom_products(summary["df_source"], summary.get("cols_source", {}))
            for a in uplift_plan_for_bottom(b5, summary.get("cols_source", {})):
                write_lines(f"- {a}")
    except Exception:
        write_lines("Provide product and revenue columns to compute uplift plan.")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Executive Sales Decision"), ln=True)
    write_lines([
        "Objective: Increase revenue while reducing dependency risk.",
        "Decision:",
        "Concentrate resources on top-performing products and customers",
        "Simultaneously reduce revenue leakage from weak products and churn",
        "Why:",
        "Sales data shows revenue is highly concentrated",
        "This creates short-term profit but long-term risk"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Product-Level Sales Strategy"), ln=True)
    write_lines(["A. Push Strategy (High Priority Products)"])
    write_lines([
        "Identify products contributing majority of revenue",
        "Increase visibility, sales incentives, availability",
        "Impact: Fast revenue growth with lowest risk"
    ])
    write_lines(["B. Fix Strategy (Medium Priority Products)"])
    write_lines([
        "Adjust pricing",
        "Improve bundling",
        "Targeted promotions (not flat discounts)",
        "Impact: Converts hidden potential into incremental revenue"
    ])
    write_lines(["C. Exit / Bundle Strategy (Low Priority Products)"])
    write_lines([
        "Low sales, low growth, high inventory cost",
        "Bundle with star products, clear inventory, stop investment",
        "Impact: Frees working capital and reduces losses"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Customer Sales Strategy"), ln=True)
    write_lines(["A. Protect High-Value Customers"])
    write_lines([
        "Priority service, loyalty benefits, relationship management",
        "Impact: Prevents sudden revenue drop"
    ])
    write_lines(["B. Win-Back Inactive Customers"])
    write_lines([
        "Personalized offers, limited-time incentives, re-engagement campaigns",
        "Impact: Cheaper than acquiring new customers"
    ])
    write_lines(["C. Reduce Dependency Risk"])
    write_lines([
        "Avoid relying on few customers",
        "Expand mid-tier customer base",
        "Impact: Stable long-term growth"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Region / Market Sales Strategy"), ln=True)
    write_lines(["A. Scale Strong Regions"])
    write_lines([
        "Allocate higher marketing budget and better sales coverage",
        "Impact: Predictable revenue expansion"
    ])
    write_lines(["B. Diagnose Weak Regions"])
    write_lines([
        "Investigate pricing mismatch, logistics delays, competitive pressure",
        "Impact: Fix issues or exit unprofitable regions"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Pricing & Discount Strategy"), ln=True)
    write_lines(["A. Stop Flat Discounts"])
    write_lines(["Flat discounts reduce margin without guaranteed volume"])
    write_lines(["B. Move to Targeted Pricing"])
    write_lines([
        "Discounts only for specific customers, regions, time windows",
        "Impact: Improves margin without hurting sales"
    ])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Sales Forecast & Planning Strategy"), ln=True)
    write_lines(["A. Use Forecast for Action, Not Reporting"])
    write_lines(["Plan inventory, manpower, promotions"])
    write_lines(["B. Prepare Scenarios"])
    write_lines(["Best case, expected case, worst case"])
    write_lines(["Impact: Reduces surprises and improves control"])

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe_text("Sales Risk Management"), ln=True)
    write_lines(["Key Risks Identified"])
    write_lines(["Revenue concentration, customer churn, dead inventory, seasonal volatility"])
    write_lines(["Risk Mitigation Actions"])
    write_lines(["Diversify mix, improve retention, reduce slow-moving stock"])
    write_lines(["Impact: Protects future revenue"])

    pdf.output(path)
    return path
