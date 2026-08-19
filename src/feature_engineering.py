import pandas as pd


def build_customer_features(
    customers,
    orders
):

    orders = orders.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    today = orders["order_date"].max()

    customer_features = (
        orders.groupby("customer_id")
        .agg(
            total_orders=(
                "order_id",
                "nunique"
            ),
            total_spend=(
                "sales",
                "sum"
            ),
            total_profit=(
                "profit",
                "sum"
            ),
            average_order_value=(
                "sales",
                "mean"
            ),
            last_purchase=(
                "order_date",
                "max"
            ),
            total_quantity=(
                "quantity",
                "sum"
            ),
        )
        .reset_index()
    )

    customer_features["days_since_last_purchase"] = (
        today -
        customer_features["last_purchase"]
    ).dt.days

    customer_features = customers.merge(
        customer_features,
        on="customer_id",
        how="left"
    )

    numeric_columns = [
        "total_orders",
        "total_spend",
        "total_profit",
        "average_order_value",
        "total_quantity",
        "days_since_last_purchase"
    ]

    for column in numeric_columns:

        customer_features[column] = (
            customer_features[column]
            .fillna(0)
        )

    customer_features["has_purchased"] = (
        customer_features["total_orders"] > 0
    ).astype(int)

    return customer_features


if __name__ == "__main__":

    customers = pd.read_csv(
        "data/processed/customers_clean.csv"
    )

    orders = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    features = build_customer_features(
        customers,
        orders
    )

    features.to_csv(
        "data/processed/customer_features.csv",
        index=False
    )

    print(features.head())