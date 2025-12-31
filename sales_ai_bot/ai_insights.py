def ai_prompt(summary, strategies):
    top_products = list(summary.get('top_products', []).index) if len(summary.get('top_products', [])) > 0 else []
    return f"""
AI Executive Summary

What changed?
- Total Revenue: {summary.get('total_revenue', 0):,.2f}
- Top Products: {top_products}

Why it changed?
- Concentration in top products and customers impacts volatility.
- Recent trend and region mix influence overall growth.

What to do next?
- Focus budget on top products.
- Retain high-value customers and win back inactive ones.
- Align pricing and promotions with discount effectiveness.
"""
