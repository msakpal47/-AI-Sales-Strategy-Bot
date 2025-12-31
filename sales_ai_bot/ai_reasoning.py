def ai_reason(segment_results):
    insights = []
    for seg, r in segment_results.items():
        tr = r["summary"].get("total_revenue", 0.0)
        cm = r.get("churn")
        risk = len(cm["customers_at_risk"]) if cm and "customers_at_risk" in cm else 0
        action = r.get("strategy", [""])[0] if r.get("strategy") else ""
        insights.append(f"{seg} segment: Revenue {tr:,.0f}, Churn risk {risk}. Action: {action}")
    return insights
