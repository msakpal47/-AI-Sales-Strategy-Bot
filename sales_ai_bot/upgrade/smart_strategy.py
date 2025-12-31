def smart_strategy(forecast, churn_count, high_value_customers):
    insights = []
    if forecast < 0:
        insights.append("Sales trend is declining. Immediate promotional campaign needed.")
    if churn_count > 10:
        insights.append("High churn risk detected. Start win-back offers for inactive customers.")
    if high_value_customers < 5:
        insights.append("Revenue concentration risk. Expand mid-tier customer base.")
    return insights
