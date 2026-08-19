import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def create_rfm(orders):
    """
    Create RFM features:

    Recency  = How recently the customer purchased
    Frequency = How often the customer purchased
    Monetary = How much the customer spent
    """

    orders = orders.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    orders = orders.dropna(
        subset=["order_date"]
    )

    reference_date = (
        orders["order_date"].max()
        + pd.Timedelta(days=1)
    )

    rfm = (
        orders.groupby("customer_id")
        .agg(
            recency=(
                "order_date",
                lambda x: (
                    reference_date - x.max()
                ).days
            ),
            frequency=(
                "order_id",
                "nunique"
            ),
            monetary=(
                "sales",
                "sum"
            )
        )
        .reset_index()
    )

    return rfm


def segment_customers(
    orders,
    number_of_clusters=5
):
    """
    Segment customers using RFM + K-Means.

    Returns a DataFrame containing:
    customer_id
    recency
    frequency
    monetary
    cluster
    segment
    """

    rfm = create_rfm(orders)

    # Make sure we have enough customers
    if len(rfm) < number_of_clusters:
        number_of_clusters = max(
            2,
            len(rfm)
        )

    features = rfm[
        [
            "recency",
            "frequency",
            "monetary"
        ]
    ].copy()

    # Prevent problems caused by missing/infinite values
    features = features.replace(
        [float("inf"), float("-inf")],
        0
    )

    features = features.fillna(0)

    # Scale the RFM variables
    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        features
    )

    # K-Means clustering
    model = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=10
    )

    rfm["cluster"] = model.fit_predict(
        scaled_features
    )

    # --------------------------------------------------------
    # Create business-friendly segment names
    # --------------------------------------------------------

    cluster_summary = (
        rfm.groupby("cluster")
        .agg(
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean")
        )
    )

    # Higher frequency and monetary are better.
    # Lower recency is better.
    cluster_summary["business_score"] = (
        cluster_summary["avg_frequency"].rank()
        +
        cluster_summary["avg_monetary"].rank()
        -
        cluster_summary["avg_recency"].rank()
    )

    clusters_sorted = (
        cluster_summary[
            "business_score"
        ]
        .sort_values(
            ascending=False
        )
        .index
        .tolist()
    )

    segment_names = [
        "VIP Customers",
        "Loyal Customers",
        "Potential Loyalists",
        "At Risk",
        "Low Value"
    ]

    cluster_to_segment = {}

    for position, cluster in enumerate(
        clusters_sorted
    ):

        if position < len(segment_names):

            cluster_to_segment[
                cluster
            ] = segment_names[position]

        else:

            cluster_to_segment[
                cluster
            ] = "Other"

    rfm["segment"] = (
        rfm["cluster"]
        .map(cluster_to_segment)
    )

    return rfm


# ============================================================
# TESTING / DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    orders = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    result = segment_customers(
        orders
    )

    print("\nCUSTOMER SEGMENTS")
    print("=" * 60)

    print(
        result["segment"]
        .value_counts()
    )

    print("\nSample:")
    print(
        result.head(10)
    )

    result.to_csv(
        "data/processed/customer_segments.csv",
        index=False
    )

    print(
        "\nSaved:"
        " data/processed/customer_segments.csv"
    )