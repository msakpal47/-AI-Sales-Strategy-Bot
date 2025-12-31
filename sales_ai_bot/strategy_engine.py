def generate_strategy(summary):
    strategies = []
    total = float(summary.get('total_revenue', 0) or 0)
    top_customers = summary.get('top_customers')
    top_products = summary.get('top_products')
    top_regions = summary.get('top_regions')

    if total > 0 and top_customers is not None and len(top_customers) > 0:
        if float(top_customers.iloc[0]) / total > 0.4:
            strategies.append("High dependency on few customers. Introduce retention and loyalty offers.")

    if total > 0 and top_products is not None and len(top_products) > 0:
        share_top3 = float(top_products.head(3).sum()) / total
        if share_top3 >= 0.5:
            strategies.append("Focus marketing on top 3 products contributing majority revenue.")
        else:
            strategies.append("Broaden product promotion. Test bundles and upsells to lift mid-tier products.")

    if total > 0 and top_regions is not None and len(top_regions) > 0:
        if float(top_regions.iloc[0]) / total > 0.35:
            strategies.append("Region-heavy revenue. Launch localized campaigns and logistics improvements in top market.")

    return strategies
