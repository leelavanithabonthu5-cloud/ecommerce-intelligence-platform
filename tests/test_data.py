import pandas as pd


def test_orders_have_positive_sales():

    df = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    assert (
        df["sales"] >= 0
    ).all()


def test_orders_have_positive_quantity():

    df = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    assert (
        df["quantity"] > 0
    ).all()


def test_customer_ids_exist():

    df = pd.read_csv(
        "data/processed/customers_clean.csv"
    )

    assert (
        df["customer_id"]
        .notna()
        .all()
    )