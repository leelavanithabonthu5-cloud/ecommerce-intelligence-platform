import os
import pandas as pd


RAW_DIR = os.path.join("data", "raw")
REPORT_DIR = os.path.join("data", "processed")


def validate_file(filepath, key_column=None):
    df = pd.read_csv(filepath)

    report = {
        "file": os.path.basename(filepath),
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_keys": 0,
    }

    if key_column and key_column in df.columns:
        report["duplicate_keys"] = int(
            df[key_column].duplicated().sum()
        )

    return report


def validate_all():

    files = {
        "customers.csv": "customer_id",
        "products.csv": "product_id",
        "orders.csv": "order_id",
        "marketing.csv": "campaign_id",
        "inventory.csv": "product_id",
    }

    reports = []

    for filename, key in files.items():

        path = os.path.join(RAW_DIR, filename)

        if os.path.exists(path):

            result = validate_file(
                path,
                key
            )

            reports.append(result)

    report_df = pd.DataFrame(reports)

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    report_df.to_csv(
        os.path.join(
            REPORT_DIR,
            "data_quality_report.csv"
        ),
        index=False
    )

    return report_df


if __name__ == "__main__":

    report = validate_all()

    print("\nDATA QUALITY REPORT")
    print("=" * 70)
    print(report.to_string(index=False))