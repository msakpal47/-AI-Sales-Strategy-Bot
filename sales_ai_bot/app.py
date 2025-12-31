import streamlit as st
st.set_page_config(page_title="AI Sales Strategy Bot", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1rem;padding-bottom:2rem;background:transparent}
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, #f7fbff 0%, #f1f5fa 100%);
}
[data-testid="stHeader"]{background:transparent}
.hero{background:linear-gradient(90deg,#005bea,#00c6fb);color:white;padding:24px 28px;border-radius:14px;margin-bottom:12px}
.hero h1{margin:0;font-size:28px}
.hero p{margin:6px 0 0 0;opacity:.95}
.card{background:#ffffff;border:1px solid #e6e9ef;border-radius:12px;padding:16px;margin:8px 0}
.upload-note{color:#0a2540;font-size:14px;margin-top:6px}
h2, h3{
  position: relative;
  background: linear-gradient(90deg, rgba(0,91,234,0.06) 0%, rgba(0,198,251,0.06) 100%);
  border: 1px solid #e6e9ef;
  padding: 10px 14px;
  border-radius: 10px;
  color: #0a2540;
}
h2::after, h3::after{
  content: "AI Sales Strategy Bot";
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #27496d;
  opacity: 0.35;
  letter-spacing: 0.5px;
}
</style>
<div class="hero">
  <h1>📊 AI Sales Strategy Bot</h1>
  <p>Decisions that grow revenue — forecast, segment, retain, and act.</p>
</div>
""", unsafe_allow_html=True)
import pandas as pd
import os
from datetime import datetime
from data_loader import load_sales_file
from profiler import detect_columns
from analysis_engine import sales_summary
from strategy_engine import generate_strategy
from dashboard import render_dashboard
from ai_insights import ai_prompt
from upgrade.forecasting import forecast_sales
from upgrade.segmentation import customer_segmentation
from upgrade.churn import churn_risk, churn_model
from upgrade.smart_strategy import smart_strategy
from analysis_engine import product_zone_analysis, customer_zone_analysis, region_zone_analysis, seasonality_analysis, price_discount_effectiveness, compute_kpis
from analysis_engine import six_month_forecast, top_bottom_products, uplift_plan_for_bottom, top5_customer_pct
from charts import create_charts
from emailer import send_report
from final_full_report import build_full_pdf
from data_health import data_health
from pattern_detector import detect_patterns as pd_detect_patterns
from auto_segmentation import auto_segment
from segment_runner import run_segments
from ai_reasoning import ai_reason
from data_understanding import build_view
from data_understanding import detect_patterns, build_segments, analyze_segment, build_view, executive_synthesis

file = st.file_uploader("Upload Sales File")
st.markdown('<div class="upload-note">Upload up to 8 GB per file</div>', unsafe_allow_html=True)

if file:
    try:
        df = load_sales_file(file)
        cols = detect_columns(df)
        st.subheader("Column Mapping")
        with st.expander("Adjust detected columns"):
            date_opt = st.selectbox("Date column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["date"])) if cols["date"] in df.columns else 0)
            revenue_opt = st.selectbox("Revenue/Amount column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["revenue"])) if cols["revenue"] in df.columns else 0)
            product_opt = st.selectbox("Product column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["product"])) if cols["product"] in df.columns else 0)
            customer_opt = st.selectbox("Customer column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["customer"])) if cols["customer"] in df.columns else 0)
            region_opt = st.selectbox("Region column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["region"])) if cols["region"] in df.columns else 0)
            discount_opt = st.selectbox("Discount column", ["<none>"] + list(df.columns), index=(1 + list(df.columns).index(cols["discount"])) if cols["discount"] in df.columns else 0)
        cols["date"] = None if date_opt == "<none>" else date_opt
        cols["revenue"] = None if revenue_opt == "<none>" else revenue_opt
        cols["product"] = None if product_opt == "<none>" else product_opt
        cols["customer"] = None if customer_opt == "<none>" else customer_opt
        cols["region"] = None if region_opt == "<none>" else region_opt
        cols["discount"] = None if discount_opt == "<none>" else discount_opt
        if not cols.get("revenue"):
            qty = cols.get("quantity")
            price = cols.get("price")
            if qty and price:
                df["revenue"] = pd.to_numeric(df[qty], errors="coerce").fillna(0) * pd.to_numeric(df[price], errors="coerce").fillna(0)
                cols["revenue"] = "revenue"
        if not cols.get("revenue"):
            st.error("Revenue/Amount column not detected. Map columns above or include a revenue column.")
        else:
            summary = sales_summary(df, cols)
            strategies = generate_strategy(summary)

            st.subheader("📈 Sales Insights")
            st.write(strategies)

            st.subheader("📊 Dashboard")
            render_dashboard(summary)

            st.header("🩺 Data Health")
            health = data_health(df, cols)
            st.write(health)

            st.header("🧠 Data Patterns Detected")
            patterns = pd_detect_patterns(df, cols)
            st.write(patterns)

            st.header("🧩 Automatic Segmentation")
            segments = auto_segment(df, cols)
            seg_names = list(segments.keys())
            segment_results = run_segments(segments, cols) if len(seg_names) > 0 else {}
            final_ai_output = ai_reason(segment_results) if len(segment_results) > 0 else []
            st.subheader("📊 Segment-wise Intelligence")
            st.write(final_ai_output)
            st.subheader("👤 Stakeholder Views")
            roles = ["CEO", "Sales Head", "Marketing", "Ops"]
            role = st.selectbox("Role", roles)
            seg_choice = st.selectbox("Segment", list(segment_results.keys())) if len(segment_results) > 0 else None
            if seg_choice:
                view = build_view(segment_results[seg_choice], role)
                st.write(view)

            st.subheader("🧠 AI Narrative")
            prompt = ai_prompt(summary, strategies)
            st.text_area("Generated Prompt", prompt, height=200)

            date_col = cols.get("date")
            revenue_col = cols.get("revenue")
            customer_col = cols.get("customer")
            product_col = cols.get("product")
            region_col = cols.get("region")
            discount_col = cols.get("discount")

            st.subheader("🔮 Forecast")
            if date_col and revenue_col:
                fc_info = forecast_sales(df, date_col, revenue_col, model="linear", val_months=3)
                st.metric("Next Month Forecast", f"{fc_info['next_month_forecast']:,.2f}")
                st.info({
                    "Model": fc_info["model"],
                    "Validation Window": fc_info["validation_window"],
                    "Forecast Accuracy (MAPE)": f"{fc_info['forecast_accuracy']}%",
                    "Baseline Accuracy": f"{fc_info['baseline_accuracy']}%",
                    "RMSE": fc_info["rmse"]
                })
            else:
                st.info("Date column not detected. Forecast unavailable.")

            st.subheader("👥 Segmentation")
            if customer_col and revenue_col:
                seg = customer_segmentation(df, customer_col, revenue_col)
                st.dataframe(seg.head(20))
            else:
                st.info("Customer column not detected. Segmentation unavailable.")

            st.subheader("⚠️ Churn Risk")
            if customer_col and date_col:
                risky = churn_risk(df, customer_col, date_col)
                churn_count = int(len(risky))
                cm = churn_model(df, customer_col, date_col)
                st.metric("Customers at Risk", len(cm["customers_at_risk"]))
                st.write({
                    "Threshold": cm["threshold"],
                    "Precision": cm["precision"],
                    "Recall": cm["recall"],
                    "Flagged Count": int(len(cm["customers_at_risk"]))
                })
                if len(cm["customers_at_risk"]) > 0:
                    st.dataframe(cm["customers_at_risk"].head(20))
            else:
                churn_count = 0
                cm = {"precision": None, "recall": None}
                st.info("Date or customer column not detected. Churn analysis unavailable.")

            st.subheader("SECTION 3 — CHURN RISK (PROBABILISTIC)")
            st.write([
                "Churn Risk Model",
                "• Algorithm: Logistic Regression",
                "• Feature: Recency (days since last purchase)",
                "• Threshold: P(churn) > 0.70"
            ])
            st.write([
                "Results",
                f"• Customers at Risk: {churn_count}",
                f"• Precision: {cm['precision']}",
                f"• Recall: {cm['recall']}"
            ])
            if customer_col and revenue_col:
                by_customer = df.groupby(customer_col)[revenue_col].sum()
                total = float(summary["total_revenue"])
                threshold = 0.05 * total if total > 0 else 0
                high_value_customers = int((by_customer >= threshold).sum())
            else:
                high_value_customers = 0

            st.subheader("🤖 Smart Strategy")
            smart = smart_strategy(fc_info["next_month_forecast"] if date_col and revenue_col else 0, churn_count, high_value_customers)
            st.write(smart)

            st.header("1️⃣ PRODUCT ZONE ANALYSIS")
            if product_col:
                from analysis_engine import product_zone_bcg
                pz = product_zone_bcg(df, product_col, revenue_col, date_col) if date_col and revenue_col else None
                if pz is not None and len(pz) > 0:
                    st.dataframe(pz)
                    stars = pz[pz["Category"] == "Star"]["Product"].tolist()
                    cows = pz[pz["Category"] == "Cash Cow"]["Product"].tolist()
                    qmarks = pz[pz["Category"] == "Question Mark"]["Product"].tolist()
                    deads = pz[pz["Category"] == "Dead"]["Product"].tolist()
                    st.write({"Star": stars, "Cash Cow": cows, "Question Mark": qmarks, "Dead": deads})
                else:
                    st.info("Insufficient data for product zone classification.")
                st.subheader("SECTION 4 — PRODUCT ZONE (BCG RULE-BASED)")
                st.write([
                    "Product Zone Classification (BCG Logic)",
                    "Rules Used:",
                    "• Revenue percentile ≥ 80% → High market share",
                    "• Growth rate > 0 → Growing",
                    "• Margin proxy used if available",
                    "Classification:"
                ])
                if pz is not None and len(pz) > 0:
                    cls = []
                    for _, r in pz.iterrows():
                        cat = r["Category"]
                        prod_name = r["Product"]
                        if cat == "Star":
                            desc = "High Share + Growth"
                        elif cat == "Cash Cow":
                            desc = "High Share + Stable"
                        elif cat == "Question Mark":
                            desc = "Low Share + Growth"
                        else:
                            desc = "Low Share + Decline"
                        cls.append(f"• {cat}: {prod_name} ({desc})")
                    st.write(cls)
            else:
                st.info("Product column not detected.")

            st.header("2️⃣ CUSTOMER ZONE ANALYSIS")
            cz = customer_zone_analysis(df, cols)
            if len(cz["by_customer"]) > 0:
                st.bar_chart(cz["by_customer"].head(20))
                st.write({"Repeat Buyers": cz["repeat_count"], "One-time Buyers": cz["one_time_count"]})
            else:
                st.info("Customer analysis unavailable.")

            st.header("3️⃣ REGION / MARKET ZONE ANALYSIS")
            rz = region_zone_analysis(df, cols)
            if len(rz["by_region"]) > 0:
                st.bar_chart(rz["by_region"])
            else:
                st.info("Region analysis unavailable.")

            st.header("4️⃣ TIME & SEASONALITY ANALYSIS")
            sa = seasonality_analysis(df, cols)
            if len(sa["monthly"]) > 0:
                st.line_chart(sa["monthly"].set_index(date_col)[revenue_col])
                st.metric("Forecast (Next Month)", f"{sa['forecast']:,.2f}")
                if sa["forecast_accuracy_mape_last3"] is not None:
                    st.metric("Forecast Accuracy (MAPE last 3)", f"{(1-sa['forecast_accuracy_mape_last3'])*100:,.1f}%")
                if sa["baseline_naive_accuracy"] is not None:
                    st.metric("Baseline Naive Accuracy", f"{sa['baseline_naive_accuracy']*100:,.1f}%")
            else:
                st.info("Seasonality unavailable.")
            st.subheader("🔮 Forecast Methodology")
            st.write([
                "Model: Linear Regression (time trend)",
                "Validation Window: Last 3 months",
                "Accuracy Metric: MAPE",
                "Baseline (Naive): last value carry-forward",
                "Usage: Directional forecast for planning"
            ])

            st.header("6️⃣ SIX-MONTH FORECAST")
            smf = six_month_forecast(df, cols)
            if len(smf) > 0:
                st.dataframe(smf)
            else:
                st.info("Insufficient data for six-month forecast.")

            st.header("5️⃣ PRICE & DISCOUNT EFFECTIVENESS")
            pe = price_discount_effectiveness(df, cols)
            if pe["scatter"] is not None:
                st.scatter_chart(pe["scatter"])
                if pe["corr"] is not None:
                    st.metric("Discount-Revenue Correlation", f"{pe['corr']:,.2f}")
            else:
                st.info("Discount column not detected.")

            st.header("8️⃣ AI STRATEGY OUTPUT")
            st.text_area("AI Executive Summary", ai_prompt(summary, strategies), height=180)

            st.header("🧠 FINAL KPI SET")
            kpis = compute_kpis(df, summary, cols)
            st.header("SECTION 1 — EXECUTIVE KPIs (CLEAN)")
            st.write({
                "Total Revenue": f"{kpis['total_revenue']:,.2f}",
                "Growth": f"{('+' if kpis['growth_pct']>=0 else '-')}{abs(kpis['growth_pct']*100):,.1f}%"
            })
            st.subheader("Revenue Concentration")
            st.write({
                "Top 5 Products %": f"{kpis['top5_products_pct']*100:,.1f}%"
            })
            if kpis.get("top5_customers_pct", 0.0) > 0.0:
                st.write({"Top 5 Customers %": f"{kpis['top5_customers_pct']*100:,.1f}%"})
            else:
                st.warning([
                    "Top 5 Customers % could not be computed reliably.",
                    "Possible causes:",
                    "• Incorrect customer ID mapping",
                    "• Non-numeric revenue column",
                    "• Sparse transactions per customer",
                    "Action Required: Verify customer and revenue columns before production use."
                ])
            if date_col and revenue_col:
                monthly = df.copy()
                monthly[revenue_col] = pd.to_numeric(monthly[revenue_col].astype(str).str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce").fillna(0)
                monthly[date_col] = pd.to_datetime(monthly[date_col], errors="coerce", infer_datetime_format=True)
                monthly = monthly.dropna(subset=[date_col])
                monthly_series = monthly.resample("ME", on=date_col)[revenue_col].sum()
                if len(monthly_series) > 0:
                    st.line_chart(monthly_series)
                else:
                    st.info("No valid dates for resampling. Check your date column format.")
            st.header("SECTION 2 — FORECAST (WITH METHOD DISCLOSURE)")
            if date_col and revenue_col:
                fc_info = forecast_sales(df, date_col, revenue_col, model="linear", val_months=3)
                st.subheader("Forecast Methodology")
                st.write([
                    f"• Model: {fc_info['model']}",
                    f"• Validation Window: {fc_info['validation_window']}",
                    "• Accuracy Metric: MAPE",
                    f"• Forecast Accuracy: {fc_info['forecast_accuracy']}%",
                    f"• Baseline (Naive): {fc_info['baseline_accuracy']}%",
                    f"• RMSE: {fc_info['rmse']}"
                ])
                st.metric("Next Month Forecast", f"{fc_info['next_month_forecast']:,.2f}")
            else:
                st.info("Date column not detected. Forecast unavailable.")
            if customer_col and revenue_col:
                top5_pct = top5_customer_pct(df, customer_col, revenue_col)
                st.metric("Top 5 Customers %", f"{top5_pct:.2f}%")
            st.subheader("Top / Bottom 5 Products")
            t5, b5 = top_bottom_products(df, cols)
            if len(t5) > 0:
                st.write("Top 5")
                st.dataframe(t5)
            if len(b5) > 0:
                st.write("Bottom 5")
                st.dataframe(b5)
                st.subheader("Uplift Strategy for Bottom 5")
                st.write(uplift_plan_for_bottom(b5, cols))
            if customer_col and revenue_col and kpis.get("top5_customers_pct", 0.0) == 0.0:
                st.error(
                    "Top 5 Customers % = 0.0%. "
                    "This usually indicates incorrect customer ID mapping, aggregation issues, "
                    "or insufficient transaction depth. Verify inputs before production use."
                )
            st.header("📌 DECISION BOARD")
            push = pd.DataFrame([])
            leak = pd.DataFrame([])
            if product_col and revenue_col and date_col:
                from analysis_engine import product_zone_bcg
                pzd = product_zone_bcg(df, product_col, revenue_col, date_col)
                if pzd is not None and len(pzd) > 0:
                    push = pzd[pzd["Category"].isin(["Star", "Question Mark"])].sort_values("Revenue", ascending=False)
                    leak = pzd[pzd["Category"] == "Dead"].sort_values("Revenue", ascending=False)
                    total_rev = float(summary.get("total_revenue", 0.0) or 0.0)
                    push_share = float(push["Revenue"].sum()) / total_rev * 100.0 if total_rev > 0 else 0.0
                    leak_share = float(leak["Revenue"].sum()) / total_rev * 100.0 if total_rev > 0 else 0.0
                    st.subheader("Products to Push")
                    st.write({"Count": int(len(push)), "Revenue Share %": round(push_share, 1)})
                    if len(push) > 0:
                        st.bar_chart(push.set_index("Product")["Revenue"])
                    st.subheader("Where Sales Are Leaking")
                    st.write({"Dead Products": int(len(leak)), "Leakage %": round(leak_share, 1)})
                    if len(leak) > 0:
                        st.bar_chart(leak.set_index("Product")["Revenue"])
                else:
                    st.info("Insufficient data for product decision board.")
            else:
                st.info("Product decision board unavailable.")
            st.subheader("Which Customers to Retain")
            if customer_col and date_col and revenue_col:
                cm2 = churn_model(df, customer_col, date_col)
                atr = cm2["customers_at_risk"]
                st.write({"At-Risk Customers": int(len(atr)), "Threshold": cm2["threshold"], "Precision": cm2["precision"], "Recall": cm2["recall"]})
                if len(atr) > 0:
                    byc = df.groupby(customer_col)[revenue_col].sum()
                    atr["Revenue"] = atr[customer_col].map(byc)
                    atr_sorted = atr.sort_values("Revenue", ascending=False)
                    st.bar_chart(atr_sorted.set_index(customer_col)["Revenue"].head(20))
                    st.dataframe(atr_sorted.head(20))
                else:
                    st.info("No customers currently flagged at risk.")
            else:
                st.info("Customer retention analysis unavailable.")
            st.subheader("What To Do Next")
            actions = []
            if len(push) > 0:
                actions.append(f"Push {list(push.head(5)['Product'])}")
            if len(leak) > 0:
                actions.append("Bundle or exit dead products")
            actions += smart
            st.write(actions)
            st.header("📄 Export Report (PDF)")
            gen = st.button("Generate Stakeholder PDF")
            if gen:
                pza = product_zone_analysis(df, cols)
                kpi2 = compute_kpis(df, summary, cols)
                fc2 = forecast_sales(df, date_col, revenue_col, model="linear", val_months=3) if date_col and revenue_col else None
                churn2 = None
                if customer_col and date_col:
                    cmx = churn_model(df, customer_col, date_col)
                    churn2 = {"count": int(len(cmx["customers_at_risk"])), "precision": cmx["precision"], "recall": cmx["recall"]}
                sections = []
                sections.insert(0, {
                    "title": "Executive Overview",
                    "kpis": {
                        "revenue": kpi2["total_revenue"],
                        "growth": kpi2["growth_pct"],
                        "forecast": fc2["next_month_forecast"] if fc2 else 0,
                        "risk": "High" if (churn2 and churn2.get("count", 0) > 0) else "Low"
                    },
                    "pagebreak": True
                })
                exec_text = [
                    f"Total Revenue: INR {kpi2['total_revenue']:,.2f}",
                    f"Growth: {kpi2['growth_pct']*100:.1f}%",
                    f"Top 5 Products %: {kpi2['top5_products_pct']*100:.1f}%"
                ]
                if kpi2.get("top5_customers_pct", 0.0) > 0.0:
                    exec_text.append(f"Top 5 Customers %: {kpi2['top5_customers_pct']*100:.1f}%")
                else:
                    exec_text.append("⚠️ Top 5 Customers % unavailable — verify customer/revenue columns.")
                sections.append({"title": "Executive KPIs", "text": exec_text, "pagebreak": True})
                if fc2:
                    sections.append({
                        "title": "Forecast Methodology & Accuracy",
                        "text": [
                            f"Model: {fc2['model']}",
                            f"Validation Window: {fc2['validation_window']}",
                            "Accuracy Metric: MAPE",
                            f"Forecast Accuracy: {fc2['forecast_accuracy']}%",
                            f"Baseline (Naive): {fc2['baseline_accuracy']}%",
                            f"RMSE: {fc2['rmse']}",
                            f"Next Month Forecast: INR {fc2['next_month_forecast']:,.2f}"
                        ],
                        "pagebreak": True
                    })
                if churn2:
                    sections.append({
                        "title": "Churn Risk (Probabilistic Model)",
                        "text": [
                            "Algorithm: Logistic Regression",
                            "Feature: Recency (days since last purchase)",
                            "Threshold: P(churn) > 0.70",
                            f"Customers at Risk: {churn2['count']}",
                            f"Precision: {churn2['precision']}",
                            f"Recall: {churn2['recall']}"
                        ],
                        "pagebreak": True
                    })
                if pza is not None and len(pza) > 0:
                    lines = []
                    for _, r in pza.iterrows():
                        cat = r.get("Category", r.get("category"))
                        prod_name = r.get("Product", r.get("product"))
                        rev_val = r.get("Revenue", r.get("revenue"))
                        lines.append(f"{cat}: {prod_name} (Revenue: {float(rev_val):,.0f})")
                    sections.append({
                        "title": "Product Zone Classification (BCG)",
                        "text": [
                            "Rules Used:",
                            "Revenue percentile ≥ 80% → High share",
                            "Growth rate > 0 → Growing",
                            "Margin proxy if available",
                            "",
                            *lines
                        ],
                        "pagebreak": True
                    })
                try:
                    segs = segments if 'segments' in locals() else build_segments(df, cols)
                    names = list(segs.keys())
                except Exception:
                    segs, names = {}, []
                if len(names) > 0:
                    for name in names[:6]:
                        data = analyze_segment(segs[name], cols)
                        tr = data["summary"].get("total_revenue", 0.0)
                        cmx = data.get("churn")
                        risk = int(len(cmx["customers_at_risk"])) if cmx and "customers_at_risk" in cmx else 0
                        sections.append({
                            "title": f"Segment — {name}",
                            "text": [
                                f"Revenue: INR {tr:,.2f}",
                                f"Risk: {risk} customers at risk"
                            ],
                            "pagebreak": True
                        })
                sections.append({"title": "AI Strategy & What To Do Next", "text": strategies + smart, "pagebreak": False})
                charts = None
                if date_col and revenue_col and product_col:
                    mdf = df.copy()
                    mdf[revenue_col] = pd.to_numeric(mdf[revenue_col].astype(str).str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce").fillna(0)
                    mdf[date_col] = pd.to_datetime(mdf[date_col], errors="coerce", infer_datetime_format=True)
                    mdf = mdf.dropna(subset=[date_col])
                    monthly_df = mdf.resample("ME", on=date_col)[revenue_col].sum().reset_index().rename(columns={date_col: "date", revenue_col: "revenue"})
                    tp = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False).head(5)
                    product_df = tp.reset_index().rename(columns={product_col: "product", revenue_col: "revenue"})
                    charts = create_charts(monthly_df, product_df)
                output_path = f"sales_ai_bot/pdf/sales_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                path = build_full_pdf(sections=sections, charts=charts, output_path=output_path, brand="AI Sales Strategy Bot")
                with open(path, "rb") as f:
                    st.download_button("Download Stakeholder PDF", f, file_name=os.path.basename(path), mime="application/pdf")
            st.header("WHAT YOU SELL (POSITIONING THAT WINS)")
            st.markdown("Don’t sell dashboards. Sell decisions.")
            st.markdown("Your product = AI-powered Sales Intelligence that increases revenue & reduces risk.")
            st.subheader("Outcome-led promise")
            st.write([
                "Identify which products to push",
                "Where sales are leaking",
                "Which customers to retain",
                "What to do next (clear actions)"
            ])
            st.header("2️⃣ OFFER PACKAGES")
            st.subheader("🟢 Starter (SMEs)")
            st.write([
                "File upload (CSV/Excel)",
                "Power BI dashboard (template-based)",
                "Monthly refresh",
                "Executive insights (1 page)",
                "Price: ₹15k–₹25k / month"
            ])
            st.subheader("🔵 Growth")
            st.write([
                "Everything in Starter",
                "Auto refresh (API/SQL)",
                "Product + customer segmentation",
                "Forecast & churn alerts",
                "Monthly review call",
                "Price: ₹40k–₹60k / month"
            ])
            st.subheader("🟣 Pro / Enterprise")
            st.write([
                "Custom KPIs + DAX",
                "Power BI App / Embed",
                "Weekly refresh",
                "Dedicated analyst support",
                "Price: ₹1L+ / month"
            ])
            st.markdown("Tip: Anchor pricing to outcomes, not features.")
            st.header("3️⃣ DELIVERY MODEL")
            st.write("Client Data → Python AI → Clean Tables → PBIX Template → Auto Refresh → Dashboard")
            st.subheader("Why margins are high")
            st.write([
                "PBIX template reused",
                "Automation runs unattended",
                "One analyst can handle many clients"
            ])
            st.header("4️⃣ SALES PITCH (30-SECOND SCRIPT)")
            st.markdown("“We don’t just show numbers. Our AI tells you which products to focus on, which customers are at risk, and how to grow next month—inside a Power BI dashboard your team already trusts.”")
            st.write("Close with a pilot: 7–14 days • One dataset • One dashboard • Discounted fee")
            st.header("5️⃣ TARGET CUSTOMERS")
            st.write([
                "Retail & Distribution",
                "D2C / E-commerce sellers",
                "Manufacturing SMEs",
                "Regional sales teams",
                "Decision-makers: Owner, Sales Head, Ops Head"
            ])
            st.header("6️⃣ GO-TO-MARKET")
            st.write([
                "LinkedIn outreach (founders & sales heads)",
                "Referrals from accountants/ERP vendors",
                "Free Sales Health Check (lead magnet)",
                "Demo using their own data"
            ])
            st.header("7️⃣ CONTRACT & RETENTION")
            st.write([
                "3–6 month minimum",
                "Monthly insights + refresh SLA",
                "Quarterly roadmap upgrades"
            ])
            st.subheader("Upsells")
            st.write([
                "Forecast accuracy improvement",
                "Territory optimization",
                "Pricing experiments",
                "Power BI Embedded"
            ])
            st.header("8️⃣ SCALE TO SAAS")
            st.write([
                "Frontend on Netlify",
                "Backend on Render/Railway",
                "Auth + billing",
                "Tiered usage (rows, refreshes)",
                "Later: Amazon Web Services for scale"
            ])
            st.header("9️⃣ PROOF YOU NEED")
            st.write([
                "1 pilot case study (before/after)",
                "2 screenshots (Exec view + Product zone)",
                "3 quantified wins (₹↑, %↓ churn, ↑ forecast)"
            ])
            st.subheader("✅ What This App Successfully Delivers")
            st.success([
                "Next-month forecast",
                "Six-month forecast",
                "Forecast accuracy shown (MAPE-based)",
                "Directionally correct predictions",
                "Business-useful recommendations",
                "Churn risk detection",
                "Strategy recommendations",
                "Executive summary",
                "Natural language explanations",
                "Strategy synthesis",
                "Modern AI-powered analytics",
                "Uplift strategy",
                "Clear what-to-do-next logic"
            ])
            st.caption("This visually proves applied Data Science capability.")
    except Exception as e:
        st.error(f"Error: {e}")
