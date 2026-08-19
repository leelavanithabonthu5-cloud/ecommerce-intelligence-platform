
import os
import joblib
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import read_table
from src.feature_engineering import build_customer_features
from src.customer_segmentation import segment_customers
from src.forecasting import forecast_revenue
from src.inventory import inventory_analysis
from src.marketing import marketing_analysis
from src.action_center import build_action_center
from src.data_upload import save_uploaded_file


from src.report_generator import (
    dataframe_to_csv,
    dataframe_to_excel,
    create_executive_report,
    create_monthly_report,
    create_product_report,
)

from src.customer_360 import (
    get_customer_profile,
    get_retention_recommendation,
)

from src.product_intelligence import (
    analyze_products,
    get_category_performance,
)

from src.recommendations import recommend_products


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5E7EB;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #E5E7EB;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    h1 {
        font-weight: 700;
    }

    h2 {
        font-weight: 650;
    }

    h3 {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    customers = read_table("customers")
    products = read_table("products")
    orders = read_table("orders")
    marketing = read_table("marketing")
    inventory = read_table("inventory")

    return customers, products, orders, marketing, inventory


# ============================================================
# CHECK DATABASE
# ============================================================
# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

database_path = os.path.join(
    PROJECT_ROOT,
    "database",
    "ecommerce.db"
)

if not os.path.isfile(database_path):

    st.error(
        f"Database not found at: {database_path}"
    )

    st.info(
        "Make sure database/ecommerce.db exists."
    )

    st.stop()

conn = sqlite3.connect(database_path)
# ============================================================
# LOAD DATABASE TABLES
# ============================================================

try:

    customers = pd.read_sql_query(
        "SELECT * FROM customers",
        conn
    )

    products = pd.read_sql_query(
        "SELECT * FROM products",
        conn
    )

    orders = pd.read_sql_query(
        "SELECT * FROM orders",
        conn
    )

    marketing = pd.read_sql_query(
        "SELECT * FROM marketing",
        conn
    )

    inventory = pd.read_sql_query(
        "SELECT * FROM inventory",
        conn
    )

except Exception as exc:

    st.error(
        f"Unable to load database tables: {exc}"
    )

    st.stop()
# ============================================================
# DATA PREPARATION
# ============================================================

if "order_date" in orders.columns:
    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce",
    )

if "campaign_date" in marketing.columns:
    marketing["campaign_date"] = pd.to_datetime(
        marketing["campaign_date"],
        errors="coerce",
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    # 🛍️ E-Commerce
    ## Intelligence Platform

    **Business Analytics & AI**
    """
)

st.sidebar.divider()

st.sidebar.caption(
    "Analytics platform for e-commerce decision making"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Customer 360",
        "Customer Segments",
        "Churn Prediction",
        "Revenue Forecast",
        "Product Intelligence",
        "Recommendations",
        "Inventory Intelligence",
        "Marketing Analytics",
        "Action Center",
        "Data Upload",
        "Reports & Downloads",
    ],
)

st.sidebar.divider()

with st.sidebar.expander("ℹ️ About this platform"):
    st.write(
        """
        This platform provides e-commerce intelligence
        across customers, products, marketing, inventory,
        revenue and retention.
        """
    )

    st.caption(
        "Built with Python • Pandas • Scikit-learn • SQL • Streamlit"
    )


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "Executive Dashboard":

    st.title("📊 Executive Dashboard")

    st.caption(
        "E-commerce performance overview and business intelligence"
    )

    min_date = orders["order_date"].min().date()
    max_date = orders["order_date"].max().date()

    selected_dates = st.date_input(
        "Select analysis period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1])

        filtered_orders = orders[
            (orders["order_date"] >= start_date)
            & (orders["order_date"] <= end_date)
        ].copy()
    else:
        filtered_orders = orders.copy()

    total_revenue = filtered_orders["sales"].sum()
    total_profit = filtered_orders["profit"].sum()
    total_orders = filtered_orders["order_id"].nunique()
    total_customers = filtered_orders["customer_id"].nunique()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    profit_margin = (
        total_profit / total_revenue * 100
        if total_revenue > 0
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("💰 Revenue", f"${total_revenue:,.2f}")
    c2.metric("📈 Profit", f"${total_profit:,.2f}")
    c3.metric("📦 Orders", f"{total_orders:,}")

    c4, c5, c6 = st.columns(3)

    c4.metric("👥 Customers", f"{total_customers:,}")
    c5.metric("🛒 Average Order Value", f"${average_order_value:,.2f}")
    c6.metric("📊 Profit Margin", f"{profit_margin:.1f}%")

    st.divider()

    st.subheader("Revenue Trend")

    daily_revenue = (
        filtered_orders
        .groupby("order_date")["sales"]
        .sum()
        .reset_index()
    )

    daily_revenue.columns = ["date", "revenue"]

    if not daily_revenue.empty:
        fig = px.line(
            daily_revenue,
            x="date",
            y="revenue",
            title="Daily Revenue",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Performance")

    monthly = filtered_orders.copy()
    monthly["month"] = (
        monthly["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_performance = (
        monthly
        .groupby("month")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            monthly_performance,
            x="month",
            y="revenue",
            title="Monthly Revenue",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            monthly_performance,
            x="month",
            y="profit",
            title="Monthly Profit",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category Performance")

    category_data = (
        filtered_orders
        .merge(
            products[["product_id", "category"]],
            on="product_id",
            how="left",
        )
        .groupby("category")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            category_data,
            x="category",
            y="revenue",
            title="Revenue by Category",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            category_data,
            x="category",
            y="profit",
            title="Profit by Category",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Regional Performance")

    region_data = (
        filtered_orders
        .groupby("region")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        region_data,
        x="region",
        y="revenue",
        title="Revenue by Region",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Products")

    top_products = (
        filtered_orders
        .groupby("product_id")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            units=("quantity", "sum"),
        )
        .reset_index()
        .merge(
            products[["product_id", "product_name", "category"]],
            on="product_id",
            how="left",
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    st.dataframe(
        top_products[
            [
                "product_name",
                "category",
                "revenue",
                "profit",
                "units",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# CUSTOMER 360
# ============================================================

elif page == "Customer 360":

    st.title("👤 Customer 360")

    st.caption(
        "Complete customer-level intelligence for personalized decision making."
    )

    customer_ids = (
        customers["customer_id"]
        .astype(str)
        .unique()
        .tolist()
    )

    selected_customer = st.selectbox(
        "Select Customer",
        customer_ids,
    )

    profile = get_customer_profile(
        selected_customer,
        customers,
        orders,
        products,
    )

    if profile is None:
        st.error("Customer not found.")
        st.stop()

    customer = profile["customer"]

    st.subheader(
        f"👤 {customer.get('customer_name', selected_customer)}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(
            f"**Customer ID:** {customer.get('customer_id', 'N/A')}"
        )
        st.write(
            f"**Region:** {customer.get('region', 'N/A')}"
        )

    with col2:
        st.write(
            f"**Email:** {customer.get('email', 'N/A')}"
        )
        st.write(
            f"**Status:** {customer.get('customer_status', 'N/A')}"
        )

    with col3:
        st.write(
            f"**Signup Date:** {customer.get('signup_date', 'N/A')}"
        )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Revenue",
        f"${profile['total_revenue']:,.2f}",
    )

    c2.metric(
        "📦 Orders",
        f"{profile['total_orders']:,}",
    )

    c3.metric(
        "🛒 Average Order",
        f"${profile['average_order_value']:,.2f}",
    )

    c4.metric(
        "📈 Profit",
        f"${profile['total_profit']:,.2f}",
    )

    st.divider()

    st.subheader("Customer Behavior")

    behavior1, behavior2, behavior3 = st.columns(3)

    behavior1.metric(
        "Days Since Purchase",
        f"{profile['days_since_purchase']:,}",
    )

    behavior2.metric(
        "Products Purchased",
        f"{len(profile['top_products']):,}",
    )

    if profile["days_since_purchase"] > 180:
        risk_text = "🔴 High Risk"
    elif profile["days_since_purchase"] > 90:
        risk_text = "🟡 Medium Risk"
    else:
        risk_text = "🟢 Low Risk"

    behavior3.metric(
        "Retention Risk",
        risk_text,
    )

    st.subheader("💡 Recommended Action")

    recommendation = get_retention_recommendation(
        profile["days_since_purchase"],
        profile["total_revenue"],
        profile["total_orders"],
    )

    st.info(recommendation)

    st.subheader("📈 Customer Spending Trend")

    monthly_spending = profile["monthly_spending"]

    if not monthly_spending.empty:
        fig = px.line(
            monthly_spending,
            x="month",
            y="revenue",
            markers=True,
            title="Monthly Customer Revenue",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "Not enough purchase history to display a spending trend."
        )

    st.subheader("🛍️ Customer's Top Products")

    top_customer_products = profile["top_products"]

    if not top_customer_products.empty:
        st.dataframe(
            top_customer_products[
                [
                    "product_name",
                    "category",
                    "units",
                    "revenue",
                    "profit",
                ]
            ].head(10),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No product purchase history available.")

    st.divider()

    st.subheader("🎯 Personalized Product Recommendations")

    recommendations = recommend_products(
        selected_customer,
        orders,
        products,
        top_n=5,
    )

    if recommendations.empty:
        st.info("No recommendations available.")
    else:
        display_recommendations = [
            c for c in [
                "product_name",
                "category",
                "selling_price",
                "recommendation_score",
                "reason",
            ]
            if c in recommendations.columns
        ]

        st.dataframe(
            recommendations[display_recommendations],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Recommendations use purchase history, preferred categories "
            "and product popularity."
        )

    st.subheader("📋 Purchase History")

    customer_orders = profile["orders"].copy()

    if not customer_orders.empty:

        display_columns = [
            "order_id",
            "order_date",
            "product_id",
            "quantity",
            "sales",
            "profit",
        ]

        available_columns = [
            column
            for column in display_columns
            if column in customer_orders.columns
        ]

        st.dataframe(
            customer_orders[
                available_columns
            ].sort_values(
                "order_date",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download Customer History",
            data=customer_orders.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=f"customer_{selected_customer}_history.csv",
            mime="text/csv",
        )


# ============================================================
# CUSTOMER SEGMENTS
# ============================================================

elif page == "Customer Segments":

    st.title("🎯 Customer Segmentation")

    st.caption(
        "Group customers according to purchasing behavior and value."
    )

    segments = segment_customers(orders)

    st.dataframe(
        segments,
        use_container_width=True,
        hide_index=True,
    )

    if "segment" in segments.columns:
        counts = (
            segments["segment"]
            .value_counts()
            .reset_index()
        )

        counts.columns = [
            "segment",
            "customers",
        ]

        fig = px.bar(
            counts,
            x="segment",
            y="customers",
            title="Customer Segments",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.download_button(
        "⬇️ Download Customer Segments",
        data=segments.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="customer_segments.csv",
        mime="text/csv",
    )


# ============================================================
# CHURN PREDICTION
# ============================================================

elif page == "Churn Prediction":

    st.title("⚠️ Customer Churn Prediction")

    st.caption(
        "Identify customers who may be at risk of leaving and "
        "prioritize retention actions."
    )

    model_path = "models/churn_model.pkl"
    metrics_path = "models/churn_metrics.csv"
    importance_path = "models/churn_feature_importance.csv"

    if not os.path.exists(model_path):
        st.warning("Churn model has not been trained yet.")
        st.code("python src\\churn_model.py")
        st.stop()

    model = joblib.load(model_path)

    features = build_customer_features(
        customers,
        orders,
    )

    feature_columns = [
        "total_orders",
        "total_spend",
        "average_order_value",
        "total_profit",
        "days_since_last_purchase",
    ]

    missing_features = [
        column
        for column in feature_columns
        if column not in features.columns
    ]

    if missing_features:
        st.error(
            "Churn feature columns are missing: "
            + ", ".join(missing_features)
        )
        st.stop()

    features["churn_probability"] = (
        model.predict_proba(
            features[feature_columns]
        )[:, 1]
    )

    def determine_risk(probability):
        if probability >= 0.70:
            return "High"
        elif probability >= 0.40:
            return "Medium"
        return "Low"

    features["risk"] = (
        features["churn_probability"]
        .apply(determine_risk)
    )

    def retention_action(row):
        if row["risk"] == "High":
            return "Immediate retention campaign"
        elif row["risk"] == "Medium":
            return "Send personalized offer"
        return "Continue engagement"

    features["recommended_action"] = (
        features.apply(
            retention_action,
            axis=1,
        )
    )

    total_customers = len(features)
    high_risk = (features["risk"] == "High").sum()
    medium_risk = (features["risk"] == "Medium").sum()
    low_risk = (features["risk"] == "Low").sum()
    average_risk = features["churn_probability"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Customers", f"{total_customers:,}")
    c2.metric("🔴 High Risk", f"{high_risk:,}")
    c3.metric("🟡 Medium Risk", f"{medium_risk:,}")
    c4.metric("Average Churn Risk", f"{average_risk:.1%}")

    st.divider()

    st.subheader("Customer Risk Scores")

    risk_filter = st.selectbox(
        "Filter by risk",
        ["All", "High", "Medium", "Low"],
    )

    display_data = features.copy()

    if risk_filter != "All":
        display_data = display_data[
            display_data["risk"] == risk_filter
        ]

    display_data = display_data.sort_values(
        "churn_probability",
        ascending=False,
    )

    churn_columns = [
        column
        for column in [
            "customer_id",
            "customer_name",
            "total_orders",
            "total_spend",
            "days_since_last_purchase",
            "churn_probability",
            "risk",
            "recommended_action",
        ]
        if column in display_data.columns
    ]

    st.dataframe(
        display_data[churn_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("🔴 Highest-Risk Customers")

    high_risk_customers = (
        features[
            features["risk"] == "High"
        ]
        .sort_values(
            "churn_probability",
            ascending=False,
        )
        .head(10)
    )

    if high_risk_customers.empty:
        st.success("No high-risk customers detected.")
    else:
        high_columns = [
            column
            for column in [
                "customer_id",
                "customer_name",
                "total_spend",
                "days_since_last_purchase",
                "churn_probability",
                "recommended_action",
            ]
            if column in high_risk_customers.columns
        ]

        st.dataframe(
            high_risk_customers[high_columns],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("🤖 Model Performance")

    if os.path.exists(metrics_path):

        metrics = pd.read_csv(metrics_path).iloc[0]

        m1, m2, m3, m4, m5 = st.columns(5)

        m1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
        m2.metric("Precision", f"{metrics['precision']:.1%}")
        m3.metric("Recall", f"{metrics['recall']:.1%}")
        m4.metric("F1 Score", f"{metrics['f1']:.1%}")
        m5.metric("ROC-AUC", f"{metrics['roc_auc']:.1%}")

    if os.path.exists(importance_path):

        st.subheader("What Drives Churn?")

        importance = pd.read_csv(
            importance_path
        )

        fig = px.bar(
            importance.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            title="Churn Feature Importance",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# REVENUE FORECAST
# ============================================================

elif page == "Revenue Forecast":

    st.title("📈 Revenue Forecast")

    st.caption(
        "Forecast future revenue from historical sales patterns."
    )

    forecast_days = st.slider(
        "Forecast horizon",
        min_value=7,
        max_value=90,
        value=30,
    )

    daily, forecast = forecast_revenue(
        orders,
        days=forecast_days,
    )

    historical = daily.copy()
    historical["type"] = "Historical"

    historical = historical.rename(
        columns={
            "date": "Date",
            "revenue": "Revenue",
        }
    )

    future = forecast.rename(
        columns={
            "date": "Date",
            "forecast_revenue": "Revenue",
        }
    )

    future["type"] = "Forecast"

    chart_data = pd.concat(
        [
            historical[["Date", "Revenue", "type"]],
            future[["Date", "Revenue", "type"]],
        ],
        ignore_index=True,
    )

    fig = px.line(
        chart_data,
        x="Date",
        y="Revenue",
        color="type",
        title="Revenue Forecast",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.dataframe(
        forecast,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PRODUCT INTELLIGENCE
# ============================================================

elif page == "Product Intelligence":

    st.title("🛍️ Product Intelligence")

    st.caption(
        "Understand product performance, profitability and demand."
    )

    product_data = analyze_products(
        orders,
        products,
    )

    total_products = len(product_data)

    star_products = (
        product_data["status"] == "Star Product"
    ).sum()

    loss_products = (
        product_data["status"] == "Loss Making"
    ).sum()

    total_product_revenue = (
        product_data["revenue"].sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Products", f"{total_products:,}")
    c2.metric("⭐ Star Products", f"{star_products:,}")
    c3.metric("⚠️ Loss Making", f"{loss_products:,}")
    c4.metric(
        "Product Revenue",
        f"${total_product_revenue:,.2f}",
    )

    st.divider()

    st.subheader("Product Performance")

    status_filter = st.selectbox(
        "Filter Products",
        [
            "All",
            "Star Product",
            "Stable",
            "Low Demand",
            "Loss Making",
        ],
    )

    filtered_products = product_data.copy()

    if status_filter != "All":
        filtered_products = filtered_products[
            filtered_products["status"] == status_filter
        ]

    st.dataframe(
        filtered_products[
            [
                "product_name",
                "category",
                "units_sold",
                "revenue",
                "profit",
                "profit_margin",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top Products by Revenue")

    top_products = (
        product_data
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_products,
        x="product_name",
        y="revenue",
        title="Top 10 Products by Revenue",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Product Profitability")

    profitability = (
        product_data
        .sort_values("profit", ascending=False)
        .head(10)
    )

    fig = px.bar(
        profitability,
        x="product_name",
        y="profit",
        title="Top 10 Products by Profit",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Category Performance")

    category_data = get_category_performance(
        orders,
        products,
    )

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        category_data,
        x="category",
        y="revenue",
        title="Revenue by Category",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.download_button(
        "⬇️ Download Product Analysis",
        data=product_data.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="product_intelligence.csv",
        mime="text/csv",
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "Recommendations":

    st.title("🎯 Product Recommendations")

    st.caption(
        "Generate personalized product recommendations for customers."
    )

    customer_ids = (
        customers["customer_id"]
        .astype(str)
        .unique()
        .tolist()
    )

    selected_customer = st.selectbox(
        "Select Customer",
        customer_ids,
    )

    recommendations = recommend_products(
        selected_customer,
        orders,
        products,
        top_n=10,
    )

    if recommendations.empty:
        st.info("No recommendations available.")
    else:
        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download Recommendations",
            data=recommendations.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                f"recommendations_{selected_customer}.csv"
            ),
            mime="text/csv",
        )


# ============================================================
# INVENTORY INTELLIGENCE
# ============================================================

elif page == "Inventory Intelligence":

    st.title("📦 Inventory Intelligence")

    st.caption(
        "Identify products requiring stock and replenishment attention."
    )

    inventory_result = inventory_analysis(
        products,
        orders,
    )

    st.dataframe(
        inventory_result,
        use_container_width=True,
        hide_index=True,
    )

    if "inventory_status" in inventory_result.columns:

        reorder_count = (
            inventory_result["inventory_status"]
            == "REORDER NOW"
        ).sum()

        c1, c2 = st.columns(2)

        c1.metric(
            "Products Requiring Reorder",
            f"{reorder_count:,}",
        )

        c2.metric(
            "Products Analyzed",
            f"{len(inventory_result):,}",
        )

        status_counts = (
            inventory_result["inventory_status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "status",
            "products",
        ]

        fig = px.bar(
            status_counts,
            x="status",
            y="products",
            title="Inventory Status",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.download_button(
        "⬇️ Download Inventory Analysis",
        data=inventory_result.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="inventory_intelligence.csv",
        mime="text/csv",
    )


# ============================================================
# MARKETING ANALYTICS
# ============================================================

elif page == "Marketing Analytics":

    st.title("📢 Marketing Analytics")

    st.caption(
        "Measure campaign performance and marketing channel ROI."
    )

    result = marketing_analysis(
        marketing
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Spend",
        f"${result['spend'].sum():,.2f}",
    )

    c2.metric(
        "Total Revenue",
        f"${result['revenue'].sum():,.2f}",
    )

    c3.metric(
        "Average ROI",
        f"{result['roi'].mean():.2f}x",
    )

    channel_performance = (
        result
        .groupby("channel")
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
            conversions=("conversions", "sum"),
        )
        .reset_index()
    )

    channel_performance["roi"] = (
        (
            channel_performance["revenue"]
            - channel_performance["spend"]
        )
        /
        channel_performance["spend"].replace(
            0,
            pd.NA,
        )
    )

    fig = px.bar(
        channel_performance,
        x="channel",
        y="roi",
        title="ROI by Marketing Channel",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.dataframe(
        channel_performance,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ACTION CENTER
# ============================================================

# ============================================================
# ACTION CENTER
# ============================================================

elif page == "Action Center":

    st.title("💡 Action Center")

    st.caption(
        "Prioritized business recommendations generated "
        "from customer, inventory and marketing intelligence."
    )

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    inventory_result = inventory_analysis(
        products,
        orders,
    )

    # --------------------------------------------------------
    # CHURN
    # --------------------------------------------------------

    churn_result = None

    model_path = "models/churn_model.pkl"

    if os.path.exists(model_path):

        try:

            model = joblib.load(model_path)

            churn_features = build_customer_features(
                customers,
                orders,
            )

            feature_columns = [
                "total_orders",
                "total_spend",
                "average_order_value",
                "total_profit",
                "days_since_last_purchase",
            ]

            churn_features[
                "churn_probability"
            ] = model.predict_proba(
                churn_features[
                    feature_columns
                ]
            )[:, 1]

            if "risk" not in churn_features.columns:

                churn_features["risk"] = (
                    churn_features[
                        "churn_probability"
                    ]
                    .apply(
                        lambda x:
                        "High"
                        if x >= 0.70
                        else (
                            "Medium"
                            if x >= 0.40
                            else "Low"
                        )
                    )
                )

            churn_result = churn_features[
                churn_features["risk"].isin(
                    [
                        "High",
                        "Medium",
                    ]
                )
            ].copy()

        except Exception as exc:

            st.warning(
                f"Churn intelligence unavailable: {exc}"
            )

    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    try:

        marketing_result = marketing_analysis(
            marketing
        )

    except Exception:

        marketing_result = None

    # --------------------------------------------------------
    # GENERATE ACTIONS
    # --------------------------------------------------------

    actions = build_action_center(
        inventory_df=inventory_result,
        churn_df=churn_result,
        marketing_df=marketing_result,
    )

    # --------------------------------------------------------
    # KPI SUMMARY
    # --------------------------------------------------------

    if actions.empty:

        st.success(
            "🎉 No immediate business actions detected."
        )

    else:

        urgent = (
            actions["priority"] == "URGENT"
        ).sum()

        high = (
            actions["priority"] == "HIGH"
        ).sum()

        medium = (
            actions["priority"] == "MEDIUM"
        ).sum()

        low = (
            actions["priority"] == "LOW"
        ).sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "🔴 Urgent",
            f"{urgent:,}"
        )

        c2.metric(
            "🟠 High Priority",
            f"{high:,}"
        )

        c3.metric(
            "🟡 Medium",
            f"{medium:,}"
        )

        c4.metric(
            "🟢 Low",
            f"{low:,}"
        )

        st.divider()

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        priority_filter = st.selectbox(
            "Filter Actions",
            [
                "All",
                "URGENT",
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
        )

        display_actions = actions.copy()

        if priority_filter != "All":

            display_actions = (
                display_actions[
                    display_actions[
                        "priority"
                    ]
                    == priority_filter
                ]
            )

        # ----------------------------------------------------
        # ACTION TABLE
        # ----------------------------------------------------

        st.subheader(
            "📋 Recommended Business Actions"
        )

        st.dataframe(
            display_actions,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # URGENT ACTIONS
        # ----------------------------------------------------

        urgent_actions = actions[
            actions["priority"].isin(
                [
                    "URGENT",
                    "HIGH",
                ]
            )
        ]

        if not urgent_actions.empty:

            st.divider()

            st.subheader(
                "🚨 Immediate Attention Required"
            )

            for _, row in urgent_actions.head(10).iterrows():

                if row["priority"] == "URGENT":

                    st.error(
                        f"🚨 **{row['issue']}**\n\n"
                        f"**Action:** {row['recommendation']}\n\n"
                        f"**Impact:** {row['impact']}"
                    )

                else:

                    st.warning(
                        f"⚠️ **{row['issue']}**\n\n"
                        f"**Action:** {row['recommendation']}\n\n"
                        f"**Impact:** {row['impact']}"
                    )

        # ----------------------------------------------------
        # ACTION BY AREA
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📊 Actions by Business Area"
        )

        area_counts = (
            actions["area"]
            .value_counts()
            .reset_index()
        )

        area_counts.columns = [
            "area",
            "actions",
        ]

        fig = px.bar(
            area_counts,
            x="area",
            y="actions",
            title="Business Actions by Area",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        st.download_button(
            "⬇️ Download Action Plan",
            data=actions.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="business_action_plan.csv",
            mime="text/csv",
        )


# ============================================================
# DATA UPLOAD
# ============================================================

elif page == "Data Upload":

    st.title("📤 Data Upload")

    st.caption(
        "Upload new business datasets for analysis."
    )

    st.info(
        "CSV files should follow the required schema."
    )

    upload_type = st.selectbox(
        "Select dataset",
        [
            "Customers",
            "Products",
            "Orders",
            "Marketing",
            "Inventory",
        ],
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
    )

    schemas = {
        "Customers": [
            "customer_id",
            "customer_name",
            "email",
            "age",
            "gender",
            "region",
            "signup_date",
            "customer_status",
        ],
        "Products": [
            "product_id",
            "product_name",
            "category",
            "unit_cost",
            "selling_price",
            "stock_quantity",
            "reorder_level",
        ],
        "Orders": [
            "order_id",
            "customer_id",
            "product_id",
            "order_date",
            "quantity",
            "unit_price",
            "discount",
            "sales",
            "cost",
            "profit",
            "region",
        ],
        "Marketing": [
            "campaign_id",
            "campaign_date",
            "channel",
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
        ],
        "Inventory": [
            "product_id",
            "stock_quantity",
            "reorder_level",
            "last_restock_date",
        ],
    }

    if uploaded_file is not None:

        st.write("### Preview")

        try:
            df, filepath = save_uploaded_file(
                uploaded_file,
                schemas[upload_type],
            )

            st.success(
                f"{upload_type} dataset uploaded successfully."
            )

            st.write(f"Rows: {len(df):,}")
            st.write(f"Columns: {len(df.columns):,}")

            st.dataframe(
                df.head(20),
                use_container_width=True,
                hide_index=True,
            )

        except Exception as exc:
            st.error(
                f"Upload failed: {exc}"
            )


# ============================================================
# REPORTS & DOWNLOADS
# ============================================================
    st.divider()

    st.subheader("🛍️ Product Performance Report")

    product_report = create_product_report(
        orders,
        products,
    )

    st.dataframe(
        product_report.head(50),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇️ Download Product Performance",
        data=dataframe_to_excel(
            product_report,
            "Product Performance",
        ),
        file_name="product_performance.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

elif page == "Reports & Downloads":

    st.title("📑 Reports & Downloads")

    st.caption(
        "Download business intelligence results for reporting and decision-making."
    )

    st.divider()

    st.subheader("📊 Executive Summary")

    executive_report = create_executive_report(
        orders,
        customers,
        products,
    )

    st.dataframe(
        executive_report,
        use_container_width=True,
        hide_index=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Download Executive CSV",
            data=dataframe_to_csv(
                executive_report
            ),
            file_name="executive_report.csv",
            mime="text/csv",
        )

    with col2:
        st.download_button(
            "⬇️ Download Executive Excel",
            data=dataframe_to_excel(
                executive_report,
                "Executive Summary",
            ),
            file_name="executive_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    st.divider()

    st.subheader("🎯 Customer Segmentation Report")

    try:
        segments = segment_customers(orders)

        st.dataframe(
            segments,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "⬇️ Download Segments CSV",
                data=dataframe_to_csv(segments),
                file_name="customer_segments.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                "⬇️ Download Segments Excel",
                data=dataframe_to_excel(
                    segments,
                    "Customer Segments",
                ),
                file_name="customer_segments.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    except Exception as exc:
        st.error(
            f"Could not generate segmentation report: {exc}"
        )

    st.divider()

    st.subheader("📦 Inventory Report")

    try:
        inventory_report = inventory_analysis(
            products,
            orders,
        )

        st.dataframe(
            inventory_report,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "⬇️ Download Inventory CSV",
                data=dataframe_to_csv(
                    inventory_report
                ),
                file_name="inventory_report.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                "⬇️ Download Inventory Excel",
                data=dataframe_to_excel(
                    inventory_report,
                    "Inventory",
                ),
                file_name="inventory_report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    except Exception as exc:
        st.error(
            f"Could not generate inventory report: {exc}"
        )

    st.divider()

    st.subheader("📢 Marketing Performance Report")

    try:
        marketing_report = marketing_analysis(
            marketing
        )

        st.dataframe(
            marketing_report,
            use_container_width=True,
            hide_index=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "⬇️ Download Marketing CSV",
                data=dataframe_to_csv(
                    marketing_report
                ),
                file_name="marketing_report.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                "⬇️ Download Marketing Excel",
                data=dataframe_to_excel(
                    marketing_report,
                    "Marketing",
                ),
                file_name="marketing_report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    except Exception as exc:
        st.error(
            f"Could not generate marketing report: {exc}"
        )

    st.divider()

    st.subheader("📈 Monthly Performance Report")

    monthly_report = create_monthly_report(
        orders
    )

    st.dataframe(
        monthly_report,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.line(
        monthly_report,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Performance",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "⬇️ Monthly CSV",
            data=dataframe_to_csv(
                monthly_report
            ),
            file_name="monthly_performance.csv",
            mime="text/csv",
        )

    with col2:

        st.download_button(
            "⬇️ Monthly Excel",
            data=dataframe_to_excel(
                monthly_report,
                "Monthly Performance",
            ),
            file_name="monthly_performance.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "E-Commerce Intelligence Platform • "
    "Portfolio Project • Built with Python & Streamlit"
)
