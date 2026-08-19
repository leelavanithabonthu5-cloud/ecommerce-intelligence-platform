import pandas as pd


def marketing_analysis(marketing):

    df = marketing.copy()

    df["spend"] = pd.to_numeric(
        df["spend"],
        errors="coerce"
    )

    df["impressions"] = pd.to_numeric(
        df["impressions"],
        errors="coerce"
    )

    df["clicks"] = pd.to_numeric(
        df["clicks"],
        errors="coerce"
    )

    df["conversions"] = pd.to_numeric(
        df["conversions"],
        errors="coerce"
    )

    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce"
    )

    df["ctr"] = (
        df["clicks"]
        /
        df["impressions"]
        .replace(0, float("nan"))
    )

    df["conversion_rate"] = (
        df["conversions"]
        /
        df["clicks"]
        .replace(0, float("nan"))
    )

    df["cost_per_conversion"] = (
        df["spend"]
        /
        df["conversions"]
        .replace(0, float("nan"))
    )

    df["roi"] = (
        (df["revenue"] - df["spend"])
        /
        df["spend"]
        .replace(0, float("nan"))
    )

    return df


if __name__ == "__main__":

    marketing = pd.read_csv(
        "data/processed/marketing_clean.csv"
    )

    result = marketing_analysis(
        marketing
    )

    result.to_csv(
        "data/processed/marketing_analysis.csv",
        index=False
    )

    print(result.head())