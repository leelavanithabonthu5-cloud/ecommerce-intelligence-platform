import pandas as pd


def get_customer_profile(
    customer_id,
    customers,
    orders,
    products
):
    """
    Generate a complete customer profile.
    """

    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    customer = customers[
        customers["customer_id"].astype(str)
        == str(customer_id)
    ]

    if customer.empty:
        return None

    customer = customer.iloc[0]

    # --------------------------------------------------------
    # CUSTOMER ORDERS
    # --------------------------------------------------------

    customer_orders = orders[
        orders["customer_id"].astype(str)
        == str(customer_id)
    ].copy()

    if customer_orders.empty:

        return {
            "customer": customer,
            "orders": customer_orders,
            "total_orders": 0,
            "total_revenue": 0,
            "total_profit": 0,
            "average_order_value": 0,
            "top_products": pd.DataFrame()
        }

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    customer_orders["order_date"] = pd.to_datetime(
        customer_orders["order_date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_orders = customer_orders[
        "order_id"
    ].nunique()

    total_revenue = customer_orders[
        "sales"
    ].sum()

    total_profit = customer_orders[
        "profit"
    ].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    top_products = (
        customer_orders
        .groupby("product_id")
        .agg(
            units=("quantity", "sum"),
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
        .merge(
            products[
                [
                    "product_id",
                    "product_name",
                    "category"
                ]
            ],
            on="product_id",
            how="left"
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    # --------------------------------------------------------
    # MONTHLY SPENDING
    # --------------------------------------------------------

    monthly_spending = customer_orders.copy()

    monthly_spending["month"] = (
        monthly_spending["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_spending = (
        monthly_spending
        .groupby("month")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # LAST PURCHASE
    # --------------------------------------------------------

    last_purchase = (
        customer_orders["order_date"]
        .max()
    )

    reference_date = (
        orders["order_date"].max()
        + pd.Timedelta(days=1)
    )

    days_since_purchase = (
        reference_date - last_purchase
    ).days

    return {

        "customer": customer,

        "orders": customer_orders,

        "total_orders": total_orders,

        "total_revenue": total_revenue,

        "total_profit": total_profit,

        "average_order_value": average_order_value,

        "top_products": top_products,

        "monthly_spending": monthly_spending,

        "last_purchase": last_purchase,

        "days_since_purchase": days_since_purchase
    }


def get_retention_recommendation(
    days_since_purchase,
    total_revenue,
    total_orders
):

    if days_since_purchase > 180:

        return (
            "🔴 High Priority: "
            "Launch a personalized win-back campaign "
            "with an exclusive offer."
        )

    if days_since_purchase > 90:

        return (
            "🟡 Medium Priority: "
            "Send a personalized product recommendation "
            "and limited-time discount."
        )

    if total_revenue > 1000:

        return (
            "🟢 VIP Opportunity: "
            "Offer loyalty rewards and early access "
            "to new products."
        )

    if total_orders >= 5:

        return (
            "🟢 Loyal Customer: "
            "Encourage repeat purchases through "
            "loyalty incentives."
        )

    return (
        "🔵 Engagement Opportunity: "
        "Use personalized recommendations to encourage "
        "the next purchase."
    )