import pandas as pd
import numpy as np


def prepare_daily_revenue(orders):

    orders = orders.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    daily = (
        orders.groupby("order_date")["sales"]
        .sum()
        .reset_index()
    )

    daily = daily.rename(
        columns={
            "order_date": "date",
            "sales": "revenue"
        }
    )

    daily = daily.sort_values(
        "date"
    )

    return daily


def forecast_revenue(
    orders,
    days=30,
    window=30
):

    daily = prepare_daily_revenue(
        orders
    )

    if len(daily) < window:
        window = max(
            7,
            len(daily) // 2
        )

    recent = daily[
        "revenue"
    ].tail(window)

    average_revenue = recent.mean()

    volatility = recent.std()

    last_date = daily["date"].max()

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=days
    )

    forecast = pd.DataFrame({
        "date": future_dates,
        "forecast_revenue": average_revenue
    })

    forecast["lower_bound"] = np.maximum(
        0,
        average_revenue -
        1.96 * volatility
    )

    forecast["upper_bound"] = (
        average_revenue +
        1.96 * volatility
    )

    return daily, forecast


if __name__ == "__main__":

    orders = pd.read_csv(
        "data/processed/orders_clean.csv"
    )

    daily, forecast = forecast_revenue(
        orders
    )

    forecast.to_csv(
        "data/processed/revenue_forecast.csv",
        index=False
    )

    print(forecast.head())