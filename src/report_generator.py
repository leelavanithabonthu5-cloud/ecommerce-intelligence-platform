import io
import pandas as pd


def dataframe_to_csv(df):
    """Convert DataFrame to downloadable CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_excel(df, sheet_name="Report"):
    """Convert DataFrame to downloadable Excel bytes."""

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name[:31]
        )

    output.seek(0)

    return output.getvalue()


def create_executive_report(
    orders,
    customers,
    products,
):
    """
    Create a high-level executive business report.
    """

    orders = orders.copy()

    if "order_date" in orders.columns:
        orders["order_date"] = pd.to_datetime(
            orders["order_date"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # CORE KPIs
    # --------------------------------------------------------

    total_revenue = (
        orders["sales"].sum()
        if "sales" in orders.columns
        else 0
    )

    total_profit = (
        orders["profit"].sum()
        if "profit" in orders.columns
        else 0
    )

    total_orders = (
        orders["order_id"].nunique()
        if "order_id" in orders.columns
        else len(orders)
    )

    total_customers = (
        orders["customer_id"].nunique()
        if "customer_id" in orders.columns
        else len(customers)
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    profit_margin = (
        total_profit / total_revenue
        if total_revenue > 0
        else 0
    )

    # --------------------------------------------------------
    # REPORT TABLE
    # --------------------------------------------------------

    report = pd.DataFrame(
        [
            {
                "Metric": "Total Revenue",
                "Value": round(total_revenue, 2),
                "Unit": "USD",
            },
            {
                "Metric": "Total Profit",
                "Value": round(total_profit, 2),
                "Unit": "USD",
            },
            {
                "Metric": "Total Orders",
                "Value": total_orders,
                "Unit": "Orders",
            },
            {
                "Metric": "Unique Customers",
                "Value": total_customers,
                "Unit": "Customers",
            },
            {
                "Metric": "Average Order Value",
                "Value": round(
                    average_order_value,
                    2
                ),
                "Unit": "USD",
            },
            {
                "Metric": "Profit Margin",
                "Value": round(
                    profit_margin * 100,
                    2
                ),
                "Unit": "%",
            },
            {
                "Metric": "Products",
                "Value": len(products),
                "Unit": "Products",
            },
        ]
    )

    return report


def create_monthly_report(orders):
    """Create monthly revenue and profit report."""

    orders = orders.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    orders["month"] = (
        orders["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        orders
        .groupby("month")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    monthly["profit_margin"] = (
        monthly["profit"]
        /
        monthly["revenue"].replace(
            0,
            pd.NA
        )
        * 100
    )

    return monthly


def create_product_report(
    orders,
    products,
):
    """Create product performance report."""

    result = (
        orders
        .groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
        )
        .reset_index()
    )

    result = result.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
            ]
        ],
        on="product_id",
        how="left"
    )

    result["profit_margin"] = (
        result["profit"]
        /
        result["revenue"].replace(
            0,
            pd.NA
        )
        * 100
    )

    return result.sort_values(
        "revenue",
        ascending=False
    )