import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def build_executive_report(data, charts, output_path, brand=None, logo_path=None):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    title_text = (brand or "AI SALES STRATEGY") + " – EXECUTIVE SUMMARY"
    story.append(Paragraph(title_text, styles["Title"]))
    if logo_path and os.path.exists(logo_path):
        story.append(Image(logo_path, width=120, height=60))
    story.append(Spacer(1, 12))
    kpi_table = Table([
        ["Total Revenue", f"INR {data['revenue']:,.0f}"],
        ["Growth Rate", f"{data['growth']*100:.1f}%"],
        ["Forecast (Next Month)", f"INR {data['forecast']:,.0f}"],
        ["Risk Level", data["risk"]]
    ], colWidths=[200, 200])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (-1,-1), "Helvetica")
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("Key Findings", styles["Heading2"]))
    for f in data.get("findings", []):
        story.append(Paragraph(f"- {f}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Sales Trend & Loss Analysis", styles["Title"]))
    story.append(Spacer(1, 12))
    if charts.get("monthly") and os.path.exists(charts["monthly"]):
        story.append(Image(charts["monthly"], width=450, height=280))
    story.append(Spacer(1, 8))
    story.append(Paragraph(data.get("sales_comment", ""), styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Product Zone Analysis", styles["Title"]))
    story.append(Spacer(1, 12))
    if charts.get("product") and os.path.exists(charts["product"]):
        story.append(Image(charts["product"], width=450, height=280))
    story.append(Spacer(1, 10))
    for p in data.get("product_actions", []):
        story.append(Paragraph(f"- {p}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Customer & Region Risk", styles["Title"]))
    for r in data.get("customer_region_risk", []):
        story.append(Paragraph(f"- {r}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("AI Strategy & Roadmap", styles["Title"]))
    for s in data.get("strategies", []):
        story.append(Paragraph(f"- {s}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Outcome-led Promise", styles["Title"]))
    for t in [
        "Identify which products to push",
        "Where sales are leaking",
        "Which customers to retain",
        "What to do next (clear actions)"
    ]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Proof You Need", styles["Title"]))
    for t in [
        "1 pilot case study (before/after)",
        "2 screenshots (Exec view + Product zone)",
        "3 quantified wins (INR up, % down churn, up forecast)"
    ]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Business Analytics Summary", styles["Title"]))
    story.append(Paragraph(f"Total Revenue: INR {data.get('revenue', 0):,.0f}", styles["Normal"]))
    story.append(Paragraph(f"Growth Trend: {data.get('growth', 0.0)*100:.1f}%", styles["Normal"]))
    story.append(Paragraph(f"Forecast (Next Month): INR {data.get('forecast', 0.0):,.0f}", styles["Normal"]))
    for f in data.get("findings", []):
        story.append(Paragraph(f"- {f}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Future Prediction", styles["Title"]))
    story.append(Paragraph("Align inventory and campaigns to the forecast while monitoring price sensitivity and regional mix.", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Market Strategy", styles["Title"]))
    for r in data.get("customer_region_risk", []):
        story.append(Paragraph(f"- {r}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Executive Sales Decision", styles["Title"]))
    story.append(Paragraph("Objective: Increase revenue while reducing dependency risk.", styles["Normal"]))
    story.append(Paragraph("Decision:", styles["Heading2"]))
    story.append(Paragraph("Concentrate resources on top-performing products and customers", styles["Normal"]))
    story.append(Paragraph("Simultaneously reduce revenue leakage from weak products and churn", styles["Normal"]))
    story.append(Paragraph("Why:", styles["Heading2"]))
    story.append(Paragraph("Sales data shows revenue is highly concentrated", styles["Normal"]))
    story.append(Paragraph("This creates short-term profit but long-term risk", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Product-Level Sales Strategy", styles["Title"]))
    story.append(Paragraph("A. Push Strategy (High Priority Products)", styles["Heading2"]))
    for t in ["Identify products contributing majority of revenue", "Increase visibility, sales incentives, availability", "Impact: Fast revenue growth with lowest risk"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("B. Fix Strategy (Medium Priority Products)", styles["Heading2"]))
    for t in ["Adjust pricing", "Improve bundling", "Targeted promotions (not flat discounts)", "Impact: Converts hidden potential into incremental revenue"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("C. Exit / Bundle Strategy (Low Priority Products)", styles["Heading2"]))
    for t in ["Low sales, low growth, high inventory cost", "Bundle with star products, clear inventory, stop investment", "Impact: Frees working capital and reduces losses"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Customer Sales Strategy", styles["Title"]))
    story.append(Paragraph("A. Protect High-Value Customers", styles["Heading2"]))
    for t in ["Priority service, loyalty benefits, relationship management", "Impact: Prevents sudden revenue drop"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("B. Win-Back Inactive Customers", styles["Heading2"]))
    for t in ["Personalized offers, limited-time incentives, re-engagement campaigns", "Impact: Cheaper than acquiring new customers"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("C. Reduce Dependency Risk", styles["Heading2"]))
    for t in ["Avoid relying on few customers", "Expand mid-tier customer base", "Impact: Stable long-term growth"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Region / Market Sales Strategy", styles["Title"]))
    story.append(Paragraph("A. Scale Strong Regions", styles["Heading2"]))
    for t in ["Allocate higher marketing budget and better sales coverage", "Impact: Predictable revenue expansion"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("B. Diagnose Weak Regions", styles["Heading2"]))
    for t in ["Investigate pricing mismatch, logistics delays, competitive pressure", "Impact: Fix issues or exit unprofitable regions"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Pricing & Discount Strategy", styles["Title"]))
    story.append(Paragraph("A. Stop Flat Discounts", styles["Heading2"]))
    story.append(Paragraph("Flat discounts reduce margin without guaranteed volume", styles["Normal"]))
    story.append(Paragraph("B. Move to Targeted Pricing", styles["Heading2"]))
    for t in ["Discounts only for specific customers, regions, time windows", "Impact: Improves margin without hurting sales"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Sales Forecast & Planning Strategy", styles["Title"]))
    story.append(Paragraph("A. Use Forecast for Action, Not Reporting", styles["Heading2"]))
    for t in ["Plan inventory", "Plan manpower", "Plan promotions"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("B. Prepare Scenarios", styles["Heading2"]))
    for t in ["Best case", "Expected case", "Worst case", "Impact: Reduces surprises and improves control"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(PageBreak())
    story.append(Paragraph("Sales Risk Management", styles["Title"]))
    story.append(Paragraph("Key Risks Identified", styles["Heading2"]))
    for t in ["Revenue concentration", "Customer churn", "Dead inventory", "Seasonal volatility"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    story.append(Paragraph("Risk Mitigation Actions", styles["Heading2"]))
    for t in ["Diversify product and customer mix", "Improve retention", "Reduce slow-moving stock", "Impact: Protects future revenue"]:
        story.append(Paragraph(f"- {t}", styles["Normal"]))
    doc.build(story)
    return output_path
