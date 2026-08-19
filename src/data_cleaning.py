import os
import pandas as pd


RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")


def clean_customers():

    path = os.path.join(
        RAW_DIR,
        "customers.csv"
    )

    df = pd.read_csv(path)

    df = df.drop_duplicates(
        subset=["customer_id"]
    )

    df["signup_date"] = pd.to_datetime(
        df["signup_date"],
        errors="coerce"
    )

    df["email"] = df["email"].fillna(
        "unknown@example.com"
    )

    df["age"] = df["age"].fillna(
        df["age"].median()
    )

    return df


def clean_products():

    path = os.path.join(
        RAW_DIR,
        "products.csv"
    )

    df = pd.read_csv(path)

    df = df.drop_duplicates(
        subset=["product_id"]
    )

    df["unit_cost"] = pd.to_numeric(
        df["unit_cost"],
        errors="coerce"
    )

    df["selling_price"] = pd.to_numeric(
        df["selling_price"],
        errors="coerce"
    )

    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"],
        errors="coerce"
    )

    df["reorder_level"] = pd.to_numeric(
        df["reorder_level"],
        errors="coerce"
    )

    df = df[
        df["selling_price"] > 0
    ]

    return df


def clean_orders():

    path = os.path.join(
        RAW_DIR,
        "orders.csv"
    )

    df = pd.read_csv(path)

    df = df.drop_duplicates(
        subset=["order_id"]
    )

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    numeric_columns = [
        "quantity",
        "unit_price",
        "discount",
        "sales",
        "cost",
        "profit"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df[
        df["quantity"] > 0
    ]

    df = df[
        df["unit_price"] > 0
    ]

    df = df.dropna(
        subset=[
            "customer_id",
            "product_id",
            "order_date"
        ]
    )

    return df


def clean_marketing():

    path = os.path.join(
        RAW_DIR,
        "marketing.csv"
    )

    df = pd.read_csv(path)

    df = df.drop_duplicates(
        subset=["campaign_id"]
    )

    df["campaign_date"] = pd.to_datetime(
        df["campaign_date"],
        errors="coerce"
    )

    numeric_columns = [
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "revenue"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def clean_inventory():

    path = os.path.join(
        RAW_DIR,
        "inventory.csv"
    )

    df = pd.read_csv(path)

    df = df.drop_duplicates(
        subset=["product_id"]
    )

    df["last_restock_date"] = pd.to_datetime(
        df["last_restock_date"],
        errors="coerce"
    )

    return df


def clean_all():

    os.makedirs(
        PROCESSED_DIR,
        exist_ok=True
    )

    customers = clean_customers()
    products = clean_products()
    orders = clean_orders()
    marketing = clean_marketing()
    inventory = clean_inventory()

    customers.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "customers_clean.csv"
        ),
        index=False
    )

    products.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "products_clean.csv"
        ),
        index=False
    )

    orders.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "orders_clean.csv"
        ),
        index=False
    )

    marketing.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "marketing_clean.csv"
        ),
        index=False
    )

    inventory.to_csv(
        os.path.join(
            PROCESSED_DIR,
            "inventory_clean.csv"
        ),
        index=False
    )

    print("Cleaning completed.")
    print(f"Customers: {len(customers):,}")
    print(f"Products: {len(products):,}")
    print(f"Orders: {len(orders):,}")
    print(f"Marketing: {len(marketing):,}")
    print(f"Inventory: {len(inventory):,}")


if __name__ == "__main__":
    clean_all()