import pandas as pd


def generate_inventory_actions(inventory_df):
    """
    Generate business actions from inventory intelligence.
    """

    actions = []

    if inventory_df is None or inventory_df.empty:
        return pd.DataFrame(
            columns=[
                "priority",
                "area",
                "issue",
                "recommendation",
                "impact",
            ]
        )

    for _, row in inventory_df.iterrows():

        product = row.get(
            "product_name",
            row.get("product_id", "Unknown Product")
        )

        status = row.get(
            "inventory_status",
            "UNKNOWN"
        )

        days = row.get(
            "days_of_inventory",
            0
        )

        reorder_qty = row.get(
            "recommended_reorder_quantity",
            0
        )

        if status == "OUT OF STOCK":

            actions.append(
                {
                    "priority": "URGENT",
                    "area": "Inventory",
                    "issue": f"{product} is out of stock",
                    "recommendation": (
                        f"Reorder approximately "
                        f"{int(reorder_qty):,} units immediately."
                    ),
                    "impact": "Potential lost sales",
                }
            )

        elif status == "REORDER NOW":

            actions.append(
                {
                    "priority": "HIGH",
                    "area": "Inventory",
                    "issue": (
                        f"{product} is below its reorder level"
                    ),
                    "recommendation": (
                        f"Reorder approximately "
                        f"{int(reorder_qty):,} units."
                    ),
                    "impact": "Stockout risk",
                }
            )

        elif status == "CRITICAL":

            actions.append(
                {
                    "priority": "HIGH",
                    "area": "Inventory",
                    "issue": (
                        f"{product} has only "
                        f"{days:.1f} days of inventory"
                    ),
                    "recommendation": (
                        f"Expedite replenishment for "
                        f"{product}."
                    ),
                    "impact": "High stockout risk",
                }
            )

        elif status == "LOW STOCK":

            actions.append(
                {
                    "priority": "MEDIUM",
                    "area": "Inventory",
                    "issue": (
                        f"{product} has low inventory"
                    ),
                    "recommendation": (
                        f"Monitor inventory and prepare "
                        f"for replenishment."
                    ),
                    "impact": "Moderate stockout risk",
                }
            )

        elif status == "OVERSTOCKED":

            actions.append(
                {
                    "priority": "LOW",
                    "area": "Inventory",
                    "issue": (
                        f"{product} appears overstocked"
                    ),
                    "recommendation": (
                        "Consider a promotion, bundle, "
                        "or pricing campaign."
                    ),
                    "impact": "Capital tied in inventory",
                }
            )

    return pd.DataFrame(actions)


def generate_churn_actions(
    churn_df,
    revenue_column="total_spend",
):
    """
    Generate retention actions for high-risk customers.
    """

    actions = []

    if churn_df is None or churn_df.empty:
        return pd.DataFrame(
            columns=[
                "priority",
                "area",
                "issue",
                "recommendation",
                "impact",
            ]
        )

    for _, row in churn_df.iterrows():

        probability = row.get(
            "churn_probability",
            0
        )

        customer = row.get(
            "customer_name",
            row.get(
                "customer_id",
                "Customer"
            )
        )

        revenue = row.get(
            revenue_column,
            0
        )

        if probability >= 0.70:

            if revenue >= 500:

                recommendation = (
                    "Launch a high-value personalized "
                    "retention campaign."
                )

            else:

                recommendation = (
                    "Send a personalized offer and "
                    "re-engagement message."
                )

            actions.append(
                {
                    "priority": "HIGH",
                    "area": "Customer Retention",
                    "issue": (
                        f"{customer} has "
                        f"{probability:.0%} churn probability"
                    ),
                    "recommendation": recommendation,
                    "impact": (
                        f"Customer value: ${revenue:,.2f}"
                    ),
                }
            )

        elif probability >= 0.40:

            actions.append(
                {
                    "priority": "MEDIUM",
                    "area": "Customer Retention",
                    "issue": (
                        f"{customer} has "
                        f"{probability:.0%} churn probability"
                    ),
                    "recommendation": (
                        "Add customer to a targeted "
                        "engagement campaign."
                    ),
                    "impact": (
                        f"Customer value: ${revenue:,.2f}"
                    ),
                }
            )

    return pd.DataFrame(actions)


def generate_marketing_actions(marketing_df):
    """
    Generate actions from marketing ROI.
    """

    actions = []

    if marketing_df is None or marketing_df.empty:
        return pd.DataFrame(
            columns=[
                "priority",
                "area",
                "issue",
                "recommendation",
                "impact",
            ]
        )

    grouped = (
        marketing_df
        .groupby("channel")
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    grouped["roi"] = (
        grouped["revenue"]
        /
        grouped["spend"].replace(
            0,
            pd.NA
        )
    )

    for _, row in grouped.iterrows():

        channel = row["channel"]
        roi = row["roi"]
        spend = row["spend"]

        if pd.isna(roi):
            continue

        if roi < 1:

            actions.append(
                {
                    "priority": "HIGH",
                    "area": "Marketing",
                    "issue": (
                        f"{channel} has ROI below 1.0x"
                    ),
                    "recommendation": (
                        "Review campaign targeting and "
                        "consider reducing spend."
                    ),
                    "impact": (
                        f"Spend: ${spend:,.2f}"
                    ),
                }
            )

        elif roi >= 3:

            actions.append(
                {
                    "priority": "LOW",
                    "area": "Marketing",
                    "issue": (
                        f"{channel} has strong ROI "
                        f"of {roi:.2f}x"
                    ),
                    "recommendation": (
                        "Consider increasing investment "
                        "while monitoring performance."
                    ),
                    "impact": (
                        f"Revenue: ${row['revenue']:,.2f}"
                    ),
                }
            )

    return pd.DataFrame(actions)


def build_action_center(
    inventory_df=None,
    churn_df=None,
    marketing_df=None,
):
    """
    Combine business actions from all intelligence modules.
    """

    frames = []

    if inventory_df is not None:
        frames.append(
            generate_inventory_actions(
                inventory_df
            )
        )

    if churn_df is not None:
        frames.append(
            generate_churn_actions(
                churn_df
            )
        )

    if marketing_df is not None:
        frames.append(
            generate_marketing_actions(
                marketing_df
            )
        )

    frames = [
        frame
        for frame in frames
        if frame is not None and not frame.empty
    ]

    if not frames:

        return pd.DataFrame(
            columns=[
                "priority",
                "area",
                "issue",
                "recommendation",
                "impact",
            ]
        )

    actions = pd.concat(
        frames,
        ignore_index=True,
    )

    priority_order = {
        "URGENT": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4,
    }

    actions["priority_order"] = (
        actions["priority"]
        .map(priority_order)
        .fillna(99)
    )

    actions = (
        actions
        .sort_values(
            "priority_order"
        )
        .drop(
            columns=["priority_order"]
        )
        .reset_index(drop=True)
    )

    return actions