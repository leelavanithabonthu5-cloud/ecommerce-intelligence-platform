
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


MODEL_DIR = "models"


FEATURE_COLUMNS = [
    "total_orders",
    "total_spend",
    "average_order_value",
    "total_profit",
    "days_since_last_purchase"
]


def prepare_churn_data(orders):

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

    features = (
        orders
        .groupby("customer_id")
        .agg(
            total_orders=(
                "order_id",
                "nunique"
            ),

            total_spend=(
                "sales",
                "sum"
            ),

            average_order_value=(
                "sales",
                "mean"
            ),

            total_profit=(
                "profit",
                "sum"
            ),

            last_purchase=(
                "order_date",
                "max"
            )
        )
        .reset_index()
    )

    features["days_since_last_purchase"] = (
        reference_date
        - features["last_purchase"]
    ).dt.days

    # --------------------------------------------------------
    # Business definition of churn
    # --------------------------------------------------------

    features["churn"] = (
        features["days_since_last_purchase"] > 180
    ).astype(int)

    return features


def train_churn_model():

    orders = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    data = prepare_churn_data(
        orders
    )

    X = data[
        FEATURE_COLUMNS
    ]

    y = data["churn"]

    if y.nunique() < 2:

        raise ValueError(
            "The churn target contains only one class. "
            "The dataset needs both churned and active customers."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = {

        "accuracy": accuracy_score(
            y_test,
            predictions
        ),

        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "roc_auc": roc_auc_score(
            y_test,
            probabilities
        )
    }

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    feature_importance = pd.DataFrame({

        "feature": FEATURE_COLUMNS,

        "importance": (
            model.feature_importances_
        )

    }).sort_values(
        "importance",
        ascending=False
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # Save model
    joblib.dump(
        model,
        os.path.join(
            MODEL_DIR,
            "churn_model.pkl"
        )
    )

    # Save metrics
    pd.DataFrame(
        [
            metrics
        ]
    ).to_csv(
        os.path.join(
            MODEL_DIR,
            "churn_metrics.csv"
        ),
        index=False
    )

    # Save feature importance
    feature_importance.to_csv(
        os.path.join(
            MODEL_DIR,
            "churn_feature_importance.csv"
        ),
        index=False
    )

    print("\nCHURN MODEL PERFORMANCE")
    print("=" * 50)

    for name, value in metrics.items():

        print(
            f"{name}: {value:.3f}"
        )

    print("\nFEATURE IMPORTANCE")
    print(
        feature_importance
    )

    print(
        "\nModel saved to models/churn_model.pkl"
    )

    return (
        model,
        metrics,
        feature_importance
    )


if __name__ == "__main__":

    train_churn_model()