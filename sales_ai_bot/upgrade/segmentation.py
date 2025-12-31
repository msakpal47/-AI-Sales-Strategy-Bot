from sklearn.cluster import KMeans

def customer_segmentation(df, customer_col, revenue_col):
    customer_sales = df.groupby(customer_col)[revenue_col].sum().reset_index()
    if len(customer_sales) == 0:
        customer_sales["segment"] = []
        return customer_sales
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    customer_sales["segment"] = kmeans.fit_predict(customer_sales[[revenue_col]])
    return customer_sales
