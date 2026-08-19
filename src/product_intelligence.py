import pandas as pd


def analyze_products(orders, products):
    """
    Generate product-level business intelligence.
    """

    orders = orders.copy()
    products = products.copy()

    # --------------------------------------------------------
    # PRODUCT PERFORMANCE
    # --------------------------------------------------------

    performance = (
        orders
        .groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # MERGE PRODUCT DETAILS
    # --------------------------------------------------------

    performance = performance.merge(
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

    # --------------------------------------------------------
    # PROFIT MARGIN
    # --------------------------------------------------------

    performance["profit_margin"] = 0.0

    mask = performance["revenue"] > 0

    performance.loc[
        mask,
        "profit_margin"
    ] = (
        performance.loc[
            mask,
            "profit"
        ]
        /
        performance.loc[
            mask,
            "revenue"
        ]
        * 100
    )

    # --------------------------------------------------------
    # REVENUE RANK
    # --------------------------------------------------------

    performance["revenue_rank"] = (
        performance["revenue"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    # --------------------------------------------------------
    # PRODUCT STATUS
    # --------------------------------------------------------

    def classify_product(row):

        if (
            row["revenue_rank"] <= 10
            and row["profit"] > 0
        ):
            return "Star Product"

        if row["profit"] < 0:
            return "Loss Making"

        if row["units_sold"] <= 5:
            return "Low Demand"

        return "Stable"

    performance["status"] = (
        performance.apply(
            classify_product,
            axis=1
        )
    )

    return performance


def get_category_performance(
    orders,
    products
):

    data = orders.merge(
        products[
            [
                "product_id",
                "category"
            ]
        ],
        on="product_id",
        how="left"
    )

    category = (
        data
        .groupby("category")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    category["profit_margin"] = (
        category["profit"]
        /
        category["revenue"]
        * 100
    )

    return category