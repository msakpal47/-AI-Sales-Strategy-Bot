import pandas as pd

def detect_columns(df):
    columns = df.columns
    date_col = next((c for c in columns if 'date' in c), None)
    revenue_col = next((c for c in columns if 'revenue' in c or 'amount' in c or 'sales' in c), None)
    product_col = next((c for c in columns if 'product' in c or 'item' in c or 'sku' in c or 'category' in c), None)
    customer_col = next((c for c in columns if 'customer' in c or 'client' in c or 'account' in c or 'buyer' in c), None)
    region_col = next((c for c in columns if 'region' in c or 'city' in c or 'state' in c or 'country' in c or 'market' in c), None)
    discount_col = next((c for c in columns if 'discount' in c or 'promo' in c), None)
    price_col = next((c for c in columns if 'price' in c or 'rate' in c or 'mrp' in c), None)
    quantity_col = next((c for c in columns if 'qty' in c or 'quantity' in c or 'units' in c or 'volume' in c), None)
    margin_col = next((c for c in columns if 'margin' in c or 'profit' in c), None)
    order_col = next((c for c in columns if 'order' in c or 'invoice' in c or 'trans' in c), None)
    if revenue_col is None and quantity_col and price_col:
        df[quantity_col] = pd.to_numeric(df[quantity_col], errors='coerce').fillna(0)
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        df["revenue"] = df[quantity_col] * df[price_col]
        revenue_col = "revenue"
    return {
        "date": date_col,
        "revenue": revenue_col,
        "product": product_col,
        "customer": customer_col,
        "region": region_col,
        "discount": discount_col,
        "price": price_col,
        "quantity": quantity_col,
        "margin": margin_col,
        "order_id": order_col
    }
