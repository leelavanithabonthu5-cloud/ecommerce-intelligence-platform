import pandas as pd


def inventory_analysis(products, orders):
    """
    Analyze inventory health using product stock,
    sales velocity, reorder levels and inventory value.
    """

    products = products.copy()
    orders = orders.copy()

    # --------------------------------------------------------
    # SALES VELOCITY
    # --------------------------------------------------------

    if "order_date" in orders.columns:
        orders["order_date"] = pd.to_datetime(
            orders["order_date"],
            errors="coerce"
        )

    sales = (
        orders
        .groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # MERGE WITH PRODUCT INFORMATION
    # --------------------------------------------------------

    columns = [
        "product_id",
        "product_name",
        "category",
        "selling_price",
        "stock_quantity",
        "reorder_level",
    ]

    available = [
        column
        for column in columns
        if column in products.columns
    ]

    inventory = products[available].copy()

    inventory = inventory.merge(
        sales,
        on="product_id",
        how="left"
    )

    inventory["units_sold"] = (
        inventory["units_sold"]
        .fillna(0)
    )

    inventory["revenue"] = (
        inventory["revenue"]
        .fillna(0)
    )

    # --------------------------------------------------------
    # DAILY SALES VELOCITY
    # --------------------------------------------------------

    if not orders.empty and "order_date" in orders.columns:

        min_date = orders["order_date"].min()
        max_date = orders["order_date"].max()

        if pd.notna(min_date) and pd.notna(max_date):

            analysis_days = (
                max_date - min_date
            ).days + 1

            analysis_days = max(
                analysis_days,
                1
            )

        else:
            analysis_days = 1

    else:
        analysis_days = 1

    inventory["daily_sales_velocity"] = (
        inventory["units_sold"]
        / analysis_days
    )

    # --------------------------------------------------------
    # DAYS OF INVENTORY REMAINING
    # --------------------------------------------------------

    inventory["days_of_inventory"] = 0.0

    velocity_mask = (
        inventory["daily_sales_velocity"] > 0
    )

    inventory.loc[
        velocity_mask,
        "days_of_inventory"
    ] = (
        inventory.loc[
            velocity_mask,
            "stock_quantity"
        ]
        /
        inventory.loc[
            velocity_mask,
            "daily_sales_velocity"
        ]
    )

    inventory.loc[
        ~velocity_mask,
        "days_of_inventory"
    ] = 999

    # --------------------------------------------------------
    # REORDER POINT
    # --------------------------------------------------------

    if "reorder_level" in inventory.columns:

        inventory["reorder_point"] = (
            inventory["reorder_level"]
            .fillna(0)
        )

    else:

        inventory["reorder_point"] = (
            inventory["daily_sales_velocity"]
            * 14
        )

    # --------------------------------------------------------
    # RECOMMENDED REORDER QUANTITY
    # --------------------------------------------------------

    target_stock_days = 30

    inventory["target_stock"] = (
        inventory["daily_sales_velocity"]
        * target_stock_days
    )

    inventory["recommended_reorder_quantity"] = (
        inventory["target_stock"]
        - inventory["stock_quantity"]
    ).clip(lower=0)

    inventory[
        "recommended_reorder_quantity"
    ] = (
        inventory[
            "recommended_reorder_quantity"
        ]
        .round()
        .astype(int)
    )

    # --------------------------------------------------------
    # INVENTORY VALUE
    # --------------------------------------------------------

    inventory["inventory_value"] = (
        inventory["stock_quantity"]
        *
        inventory["selling_price"]
    )

    # --------------------------------------------------------
    # INVENTORY STATUS
    # --------------------------------------------------------

    def get_status(row):

        stock = row["stock_quantity"]
        reorder = row["reorder_point"]
        days = row["days_of_inventory"]

        if stock <= 0:
            return "OUT OF STOCK"

        if stock <= reorder:
            return "REORDER NOW"

        if days <= 7:
            return "CRITICAL"

        if days <= 14:
            return "LOW STOCK"

        if days >= 90:
            return "OVERSTOCKED"

        return "HEALTHY"

    inventory["inventory_status"] = (
        inventory.apply(
            get_status,
            axis=1
        )
    )

    # --------------------------------------------------------
    # STOCKOUT RISK
    # --------------------------------------------------------

    def get_risk(status):

        if status in [
            "OUT OF STOCK",
            "REORDER NOW",
            "CRITICAL",
        ]:
            return "High"

        if status == "LOW STOCK":
            return "Medium"

        return "Low"

    inventory["stockout_risk"] = (
        inventory["inventory_status"]
        .apply(get_risk)
    )

    # --------------------------------------------------------
    # SORT BY RISK
    # --------------------------------------------------------

    priority = {
        "OUT OF STOCK": 1,
        "REORDER NOW": 2,
        "CRITICAL": 3,
        "LOW STOCK": 4,
        "HEALTHY": 5,
        "OVERSTOCKED": 6,
    }

    inventory["priority"] = (
        inventory["inventory_status"]
        .map(priority)
        .fillna(99)
    )

    inventory = inventory.sort_values(
        [
            "priority",
            "days_of_inventory",
        ]
    )

    inventory = inventory.drop(
        columns=["priority"]
    )

    return inventory