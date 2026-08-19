import pandas as pd


def recommend_products(
    customer_id,
    orders,
    products,
    top_n=5
):
    """
    Recommend products based on customer purchase history.

    Strategy:
    1. Identify products already purchased.
    2. Find categories the customer prefers.
    3. Rank products within preferred categories.
    4. Exclude products already purchased.
    """

    orders = orders.copy()
    products = products.copy()

    customer_orders = orders[
        orders["customer_id"].astype(str)
        == str(customer_id)
    ].copy()

    # --------------------------------------------------------
    # No purchase history
    # --------------------------------------------------------

    if customer_orders.empty:

        recommendations = (
            orders
            .groupby("product_id")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("sales", "sum")
            )
            .reset_index()
            .merge(
                products[
                    [
                        "product_id",
                        "product_name",
                        "category",
                        "selling_price"
                    ]
                ],
                on="product_id",
                how="left"
            )
            .sort_values(
                "revenue",
                ascending=False
            )
            .head(top_n)
        )

        recommendations["reason"] = (
            "Popular product"
        )

        return recommendations

    # --------------------------------------------------------
    # Products already purchased
    # --------------------------------------------------------

    purchased_products = set(
        customer_orders[
            "product_id"
        ].astype(str)
    )

    # --------------------------------------------------------
    # Preferred categories
    # --------------------------------------------------------

    customer_category = (
        customer_orders
        .merge(
            products[
                [
                    "product_id",
                    "category"
                ]
            ],
            on="product_id",
            how="left"
        )
        .groupby("category")
        .agg(
            customer_revenue=(
                "sales",
                "sum"
            ),
            customer_units=(
                "quantity",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "customer_revenue",
            ascending=False
        )
    )

    preferred_categories = (
        customer_category[
            "category"
        ]
        .head(3)
        .tolist()
    )

    # --------------------------------------------------------
    # Overall product popularity
    # --------------------------------------------------------

    product_stats = (
        orders
        .groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
    )

    product_stats = product_stats.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
                "selling_price"
            ]
        ],
        on="product_id",
        how="left"
    )

    # --------------------------------------------------------
    # Remove purchased products
    # --------------------------------------------------------

    product_stats = product_stats[
        ~product_stats[
            "product_id"
        ].astype(str).isin(
            purchased_products
        )
    ]

    # --------------------------------------------------------
    # Score products
    # --------------------------------------------------------

    product_stats["category_match"] = (
        product_stats["category"]
        .isin(
            preferred_categories
        )
        .astype(int)
    )

    # Normalize metrics
    def normalize(series):

        if series.max() == series.min():

            return pd.Series(
                0.5,
                index=series.index
            )

        return (
            (series - series.min())
            /
            (series.max() - series.min())
        )

    product_stats["revenue_score"] = normalize(
        product_stats["revenue"]
    )

    product_stats["popularity_score"] = normalize(
        product_stats["units_sold"]
    )

    # --------------------------------------------------------
    # Recommendation score
    # --------------------------------------------------------

    product_stats["recommendation_score"] = (
        product_stats["category_match"] * 0.50
        +
        product_stats["revenue_score"] * 0.30
        +
        product_stats["popularity_score"] * 0.20
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    recommendations = (
        product_stats
        .sort_values(
            "recommendation_score",
            ascending=False
        )
        .head(top_n)
        .copy()
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    recommendations["reason"] = (
        recommendations["category_match"]
        .map(
            {
                1: "Matches customer's preferred category",
                0: "Popular product"
            }
        )
    )

    return recommendations[
        [
            "product_id",
            "product_name",
            "category",
            "selling_price",
            "recommendation_score",
            "reason"
        ]
    ]