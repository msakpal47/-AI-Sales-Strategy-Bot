import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from ai_chart_insights import chart_insight
SPACE = Spacer(1, 6)

def _safe_html(text):
    if text is None:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\n", "<br/>")
    return text

def build_full_pdf(sections, charts, output_path, brand=None, logo_path=None):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    styles = getSampleStyleSheet()
    story = []

    if brand:
        story.append(Paragraph(_safe_html(brand), styles["Title"]))
        if logo_path and os.path.exists(logo_path):
            story.append(Image(logo_path, width=120, height=60))
        story.append(SPACE)

    def title(txt):
        story.append(Paragraph(f"<b>{_safe_html(txt)}</b>", styles["Title"]))
        story.append(SPACE)

    def h(txt):
        story.append(Paragraph(f"<b>{_safe_html(txt)}</b>", styles["Heading2"]))
        story.append(SPACE)

    def p(txt):
        story.append(Paragraph(_safe_html(txt), styles["Normal"]))
        story.append(SPACE)

    def kpi_cards(kpis):
        data = [
            ["Total Revenue", "Growth", "Forecast (Next Month)", "Churn Risk"],
            [
                f"INR {kpis.get('revenue', 0):,.0f}",
                f"{kpis.get('growth', 0.0)*100:.1f}%",
                f"INR {kpis.get('forecast', 0):,.0f}",
                str(kpis.get('risk', 'Low'))
            ]
        ]
        t = Table(data, colWidths=[130, 110, 150, 90])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0a2540")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
            ("BACKGROUND", (0,1), (-1,1), colors.whitesmoke),
            ("FONT", (0,1), (-1,1), "Helvetica-Bold"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("BOX", (0,0), (-1,-1), 1, colors.grey),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("TOPPADDING", (0,0), (-1,-1), 14),
        ]))
        story.append(t)
        story.append(SPACE)

    for sec in sections or []:
        if "kpis" in sec:
            kpi_cards(sec["kpis"])
        title(sec.get("title", ""))
        for block in sec.get("text", []):
            p(block)
        img_path = sec.get("image")
        if isinstance(img_path, str) and os.path.exists(img_path):
            story.append(Image(img_path, width=440, height=220))
            story.append(SPACE)
        if sec.get("pagebreak"):
            story.append(PageBreak())

    if charts and isinstance(charts, dict):
        title("Sales Visual Insights")
        count = 0
        for label, obj in charts.items():
            img = obj.get("path")
            df_ref = obj.get("df")
            story.append(Paragraph(f"<b>{_safe_html(label)}</b>", styles["Heading2"]))
            story.append(SPACE)
            if isinstance(img, str) and os.path.exists(img):
                story.append(Image(img, width=440, height=220))
                story.append(SPACE)
            if df_ref is not None:
                story.append(Paragraph(f"<i>Insight:</i> {_safe_html(chart_insight(label, df_ref))}", styles["Normal"]))
                story.append(SPACE)
            count += 1
            if count % 2 == 0:
                story.append(PageBreak())

    SimpleDocTemplate(output_path, pagesize=A4).build(story)
    return output_path
