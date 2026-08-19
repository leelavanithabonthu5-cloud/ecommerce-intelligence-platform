import os
import pandas as pd


UPLOAD_DIR = "data/uploads"


def save_uploaded_file(
    uploaded_file,
    expected_columns=None
):

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    df = pd.read_csv(
        uploaded_file
    )

    if expected_columns:

        missing_columns = [
            column
            for column in expected_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

    filepath = os.path.join(
        UPLOAD_DIR,
        uploaded_file.name
    )

    df.to_csv(
        filepath,
        index=False
    )

    return df, filepath