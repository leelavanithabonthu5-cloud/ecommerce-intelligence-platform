import os
import pandas as pd
from sqlalchemy import create_engine


DATABASE_PATH = os.path.join(
    "database",
    "ecommerce.db"
)

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


def get_engine():

    os.makedirs(
        "database",
        exist_ok=True
    )

    return create_engine(
        DATABASE_URL
    )


def load_database():

    engine = get_engine()

    files = {
        "customers": "customers_clean.csv",
        "products": "products_clean.csv",
        "orders": "orders_clean.csv",
        "marketing": "marketing_clean.csv",
        "inventory": "inventory_clean.csv",
    }

    for table, filename in files.items():

        path = os.path.join(
            "data",
            "processed",
            filename
        )

        df = pd.read_csv(path)

        df.to_sql(
            table,
            engine,
            if_exists="replace",
            index=False
        )

        print(
            f"Loaded {table}: {len(df):,} rows"
        )

    print("\nDatabase created successfully.")


def read_table(table_name):

    engine = get_engine()

    return pd.read_sql(
        f"SELECT * FROM {table_name}",
        engine
    )


if __name__ == "__main__":
    load_database()