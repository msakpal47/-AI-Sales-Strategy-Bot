import streamlit as st

def render_dashboard(summary):
    st.metric("Total Revenue", f"{summary['total_revenue']:,.2f}")
    if len(summary.get("top_products", [])) > 0:
        st.bar_chart(summary["top_products"])
    if len(summary.get("top_customers", [])) > 0:
        st.bar_chart(summary["top_customers"])
    if len(summary.get("top_regions", [])) > 0:
        st.bar_chart(summary["top_regions"])
