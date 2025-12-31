import pandas as pd

def detect_columns(df):
    columns = df.columns
    date_candidates = ['date', 'order_date', 'invoice_date', 'transaction_date', 'posting_date', 'period', 'month']
    revenue_candidates = ['revenue', 'amount', 'sales', 'net', 'total', 'turnover', 'gmv', 'sale_value']
    product_candidates = ['product', 'item', 'sku', 'category', 'product_name']
    customer_candidates = ['customer', 'client', 'account', 'buyer', 'cust', 'customer_id', 'customername']
    region_candidates = ['region', 'city', 'state', 'country', 'market', 'area', 'zone', 'location', 'outlet']
    discount_candidates = ['discount', 'promo', 'promotion', 'disc']
    price_candidates = ['price', 'rate', 'mrp', 'unit_price']
    quantity_candidates = ['qty', 'quantity', 'units', 'volume', 'qnty']
    margin_candidates = ['margin', 'profit', 'gross_margin']
    order_candidates = ['order', 'invoice', 'trans', 'transaction_id', 'order_id', 'bill_no']

    def pick(cands):
        return next((c for c in columns if any(k in c for k in cands)), None)

    date_col = pick(date_candidates)
    revenue_col = pick(revenue_candidates)
    product_col = pick(product_candidates)
    customer_col = pick(customer_candidates)
    region_col = pick(region_candidates)
    discount_col = pick(discount_candidates)
    price_col = pick(price_candidates)
    quantity_col = pick(quantity_candidates)
    margin_col = pick(margin_candidates)
    order_col = pick(order_candidates)

    if revenue_col is None and quantity_col and price_col:
        q = pd.to_numeric(df[quantity_col], errors='coerce').fillna(0)
        p = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        df["revenue"] = q * p
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
