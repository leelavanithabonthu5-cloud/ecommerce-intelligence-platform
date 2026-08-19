"""
E-Commerce Intelligence Platform
Synthetic Business Data Generator

Generates:
- Customers
- Products
- Orders
- Marketing campaigns
- Inventory

The data is synthetic and intended for portfolio/demo purposes.
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 150
NUM_ORDERS = 50_000
NUM_CAMPAIGNS = 100

OUTPUT_DIR = os.path.join("data", "raw")

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    """Return a random date between two dates."""

    delta = end_date - start_date
    random_days = random.randint(0, delta.days)

    return start_date + timedelta(days=random_days)


def money(value):
    """Round monetary value to two decimal places."""

    return round(float(value), 2)


# ============================================================
# CUSTOMER DATA
# ============================================================

def generate_customers(num_customers=NUM_CUSTOMERS):

    print("Generating customers...")

    first_names = [
        "Aarav", "Aanya", "Arjun", "Ananya", "Rahul",
        "Priya", "Rohan", "Sneha", "Vikram", "Neha",
        "Aditya", "Ishita", "Karan", "Meera", "Nikhil",
        "Pooja", "Sanjay", "Kavya", "Varun", "Divya",
        "Daniel", "Olivia", "James", "Emma", "Michael",
        "Sophia", "William", "Isabella", "David", "Mia"
    ]

    last_names = [
        "Sharma", "Patel", "Reddy", "Kumar", "Singh",
        "Verma", "Gupta", "Rao", "Mehta", "Nair",
        "Iyer", "Das", "Joshi", "Kapoor", "Malhotra",
        "Brown", "Smith", "Johnson", "Williams", "Davis",
        "Miller", "Wilson", "Moore", "Taylor", "Anderson"
    ]

    cities_by_region = {
        "North": [
            "Delhi", "Jaipur", "Lucknow", "Chandigarh",
            "Amritsar", "Dehradun"
        ],
        "South": [
            "Hyderabad", "Bengaluru", "Chennai",
            "Kochi", "Coimbatore", "Mysuru"
        ],
        "East": [
            "Kolkata", "Bhubaneswar", "Patna",
            "Ranchi", "Guwahati"
        ],
        "West": [
            "Mumbai", "Pune", "Ahmedabad",
            "Surat", "Goa", "Nagpur"
        ]
    }

    regions = list(cities_by_region.keys())

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)

    customers = []

    for i in range(1, num_customers + 1):

        region = random.choice(regions)
        city = random.choice(cities_by_region[region])

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        customer_id = f"C{i:05d}"

        name = f"{first_name} {last_name}"

        email = (
            f"{first_name.lower()}."
            f"{last_name.lower()}"
            f"{i}@example.com"
        )

        age = int(np.clip(np.random.normal(35, 10), 18, 70))

        gender = random.choice(
            ["Male", "Female", "Other"]
        )

        signup_date = random_date(
            start_date,
            datetime(2025, 6, 30)
        )

        status = random.choices(
            ["Active", "Inactive"],
            weights=[0.82, 0.18],
            k=1
        )[0]

        customers.append({
            "customer_id": customer_id,
            "customer_name": name,
            "email": email,
            "age": age,
            "gender": gender,
            "city": city,
            "region": region,
            "signup_date": signup_date.date(),
            "customer_status": status
        })

    df = pd.DataFrame(customers)

    print(f"✓ {len(df):,} customers created")

    return df


# ============================================================
# PRODUCT DATA
# ============================================================

def generate_products(num_products=NUM_PRODUCTS):

    print("Generating products...")

    product_templates = {
        "Electronics": [
            "Wireless Headphones",
            "Bluetooth Speaker",
            "Smartphone",
            "Laptop",
            "Mechanical Keyboard",
            "Wireless Mouse",
            "Smart Watch",
            "Tablet",
            "USB-C Hub",
            "Power Bank"
        ],

        "Furniture": [
            "Office Chair",
            "Study Desk",
            "Bookshelf",
            "Coffee Table",
            "Dining Chair",
            "Standing Desk",
            "Bedside Table",
            "Storage Cabinet"
        ],

        "Clothing": [
            "T-Shirt",
            "Jeans",
            "Hoodie",
            "Jacket",
            "Sneakers",
            "Formal Shirt",
            "Casual Dress",
            "Sports Shorts"
        ],

        "Home & Kitchen": [
            "Coffee Maker",
            "Air Fryer",
            "Mixer Grinder",
            "Cookware Set",
            "Water Bottle",
            "Dinner Set",
            "Storage Container",
            "Electric Kettle"
        ],

        "Sports": [
            "Yoga Mat",
            "Dumbbells",
            "Running Shoes",
            "Football",
            "Cricket Bat",
            "Tennis Racket",
            "Skipping Rope",
            "Gym Bag"
        ],

        "Beauty": [
            "Face Cream",
            "Shampoo",
            "Perfume",
            "Face Wash",
            "Hair Serum",
            "Body Lotion",
            "Makeup Kit"
        ],

        "Books": [
            "Business Book",
            "Programming Book",
            "Novel",
            "Self Help Book",
            "Children's Book",
            "Data Science Book"
        ],

        "Accessories": [
            "Backpack",
            "Wallet",
            "Sunglasses",
            "Travel Bag",
            "Phone Case",
            "Watch Strap"
        ]
    }

    category_ranges = {
        "Electronics": (40, 1500),
        "Furniture": (50, 900),
        "Clothing": (15, 250),
        "Home & Kitchen": (20, 500),
        "Sports": (15, 400),
        "Beauty": (10, 180),
        "Books": (8, 80),
        "Accessories": (10, 250)
    }

    categories = list(product_templates.keys())

    suppliers = [
        "TechSupplier",
        "Global Traders",
        "Prime Distribution",
        "Metro Wholesale",
        "Direct Imports",
        "Urban Supply"
    ]

    products = []

    for i in range(1, num_products + 1):

        category = random.choice(categories)

        base_name = random.choice(
            product_templates[category]
        )

        product_name = f"{base_name} {i}"

        low, high = category_ranges[category]

        selling_price = round(
            np.random.uniform(low, high),
            2
        )

        unit_cost = round(
            selling_price * np.random.uniform(0.45, 0.75),
            2
        )

        stock_quantity = random.randint(10, 500)

        reorder_level = random.randint(20, 100)

        supplier = random.choice(suppliers)

        product_id = f"P{i:04d}"

        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "supplier": supplier,
            "unit_cost": unit_cost,
            "selling_price": selling_price,
            "stock_quantity": stock_quantity,
            "reorder_level": reorder_level
        })

    df = pd.DataFrame(products)

    print(f"✓ {len(df):,} products created")

    return df


# ============================================================
# ORDER DATA
# ============================================================

def generate_orders(
    customers,
    products,
    num_orders=NUM_ORDERS
):

    print("Generating orders...")

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    payment_methods = [
        "Credit Card",
        "Debit Card",
        "UPI",
        "PayPal",
        "Cash on Delivery"
    ]

    customer_ids = customers["customer_id"].tolist()

    # Some customers are intentionally more active
    customer_weights = np.random.exponential(
        scale=1.0,
        size=len(customer_ids)
    )

    customer_weights = (
        customer_weights /
        customer_weights.sum()
    )

    product_ids = products["product_id"].tolist()

    product_weights = np.random.exponential(
        scale=1.0,
        size=len(product_ids)
    )

    product_weights = (
        product_weights /
        product_weights.sum()
    )

    orders = []

    for i in range(1, num_orders + 1):

        customer_id = np.random.choice(
            customer_ids,
            p=customer_weights
        )

        product_id = np.random.choice(
            product_ids,
            p=product_weights
        )

        product = products[
            products["product_id"] == product_id
        ].iloc[0]

        customer = customers[
            customers["customer_id"] == customer_id
        ].iloc[0]

        order_date = random_date(
            start_date,
            end_date
        )

        quantity = random.choices(
            [1, 2, 3, 4, 5],
            weights=[50, 25, 15, 7, 3],
            k=1
        )[0]

        unit_price = float(
            product["selling_price"]
        )

        discount = random.choice(
            [0, 0.05, 0.10, 0.15, 0.20]
        )

        gross_sales = quantity * unit_price

        sales = gross_sales * (1 - discount)

        cost = (
            quantity *
            float(product["unit_cost"])
        )

        profit = sales - cost

        orders.append({
            "order_id": f"O{i:06d}",
            "customer_id": customer_id,
            "product_id": product_id,
            "order_date": order_date.date(),
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "discount": discount,
            "sales": money(sales),
            "cost": money(cost),
            "profit": money(profit),
            "payment_method": random.choice(
                payment_methods
            ),
            "region": customer["region"]
        })

    df = pd.DataFrame(orders)

    print(f"✓ {len(df):,} orders created")

    return df


# ============================================================
# MARKETING DATA
# ============================================================

def generate_marketing_campaigns(
    num_campaigns=NUM_CAMPAIGNS
):

    print("Generating marketing campaigns...")

    channels = [
        "Google Ads",
        "Facebook",
        "Instagram",
        "Email",
        "YouTube",
        "Organic"
    ]

    campaign_names = [
        "Summer Sale",
        "Winter Sale",
        "New Customer Campaign",
        "Festival Campaign",
        "Weekend Offer",
        "Flash Sale",
        "Black Friday",
        "Holiday Campaign",
        "Product Launch",
        "Loyalty Campaign"
    ]

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    campaigns = []

    for i in range(1, num_campaigns + 1):

        channel = random.choice(channels)

        campaign_date = random_date(
            start_date,
            end_date
        )

        spend = round(
            np.random.uniform(500, 15000),
            2
        )

        impressions = random.randint(
            10_000,
            500_000
        )

        ctr = np.random.uniform(
            0.01,
            0.08
        )

        clicks = int(
            impressions * ctr
        )

        conversion_rate = np.random.uniform(
            0.02,
            0.15
        )

        conversions = int(
            clicks * conversion_rate
        )

        revenue_multiplier = np.random.uniform(
            1.2,
            5.5
        )

        revenue = round(
            spend * revenue_multiplier,
            2
        )

        campaign_name = (
            f"{random.choice(campaign_names)} "
            f"{i}"
        )

        campaigns.append({
            "campaign_id": f"M{i:04d}",
            "campaign_name": campaign_name,
            "channel": channel,
            "campaign_date": campaign_date.date(),
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue
        })

    df = pd.DataFrame(campaigns)

    print(
        f"✓ {len(df):,} marketing campaigns created"
    )

    return df


# ============================================================
# INVENTORY DATA
# ============================================================

def generate_inventory(products):

    print("Generating inventory...")

    suppliers = [
        "TechSupplier",
        "Global Traders",
        "Prime Distribution",
        "Metro Wholesale",
        "Direct Imports",
        "Urban Supply"
    ]

    inventory = []

    for _, product in products.iterrows():

        stock_quantity = int(
            product["stock_quantity"]
        )

        reorder_level = int(
            product["reorder_level"]
        )

        lead_time_days = random.randint(
            2,
            21
        )

        last_restock = random_date(
            datetime(2025, 1, 1),
            datetime(2025, 12, 31)
        )

        inventory.append({
            "product_id": product["product_id"],
            "stock_quantity": stock_quantity,
            "reorder_level": reorder_level,
            "supplier": random.choice(suppliers),
            "lead_time_days": lead_time_days,
            "last_restock_date": last_restock.date()
        })

    df = pd.DataFrame(inventory)

    print(
        f"✓ {len(df):,} inventory records created"
    )

    return df


# ============================================================
# ADD CONTROLLED DATA QUALITY ISSUES
# ============================================================

def add_data_quality_issues(
    customers,
    orders
):

    print("Adding controlled data-quality issues...")

    # --------------------------------------------------------
    # Missing customer email
    # --------------------------------------------------------

    missing_email_count = 50

    missing_email_indices = np.random.choice(
        customers.index,
        size=missing_email_count,
        replace=False
    )

    customers.loc[
        missing_email_indices,
        "email"
    ] = np.nan

    # --------------------------------------------------------
    # Duplicate orders
    # --------------------------------------------------------

    duplicate_count = 50

    duplicates = orders.sample(
        duplicate_count,
        random_state=RANDOM_SEED
    )

    orders = pd.concat(
        [orders, duplicates],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Invalid quantities
    # --------------------------------------------------------

    invalid_indices = np.random.choice(
        orders.index,
        size=10,
        replace=False
    )

    orders.loc[
        invalid_indices,
        "quantity"
    ] = -1

    print("✓ Controlled data-quality issues added")

    return customers, orders


# ============================================================
# SAVE DATA
# ============================================================

def save_data(
    customers,
    products,
    orders,
    marketing,
    inventory
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    customers_path = os.path.join(
        OUTPUT_DIR,
        "customers.csv"
    )

    products_path = os.path.join(
        OUTPUT_DIR,
        "products.csv"
    )

    orders_path = os.path.join(
        OUTPUT_DIR,
        "orders.csv"
    )

    marketing_path = os.path.join(
        OUTPUT_DIR,
        "marketing.csv"
    )

    inventory_path = os.path.join(
        OUTPUT_DIR,
        "inventory.csv"
    )

    customers.to_csv(
        customers_path,
        index=False
    )

    products.to_csv(
        products_path,
        index=False
    )

    orders.to_csv(
        orders_path,
        index=False
    )

    marketing.to_csv(
        marketing_path,
        index=False
    )

    inventory.to_csv(
        inventory_path,
        index=False
    )

    print("\nFiles saved successfully:")

    print(f"✓ {customers_path}")
    print(f"✓ {products_path}")
    print(f"✓ {orders_path}")
    print(f"✓ {marketing_path}")
    print(f"✓ {inventory_path}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("E-COMMERCE INTELLIGENCE PLATFORM")
    print("Synthetic Data Generator")
    print("=" * 60)

    customers = generate_customers()

    products = generate_products()

    orders = generate_orders(
        customers,
        products
    )

    marketing = generate_marketing_campaigns()

    inventory = generate_inventory(
        products
    )

    customers, orders = add_data_quality_issues(
        customers,
        orders
    )

    save_data(
        customers,
        products,
        orders,
        marketing,
        inventory
    )

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETED")
    print("=" * 60)

    print(f"Customers : {len(customers):,}")
    print(f"Products  : {len(products):,}")
    print(f"Orders    : {len(orders):,}")
    print(f"Campaigns : {len(marketing):,}")
    print(f"Inventory : {len(inventory):,}")


if __name__ == "__main__":
    main()