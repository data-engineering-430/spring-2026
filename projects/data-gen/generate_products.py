import csv
import random
from faker import Faker

fake = Faker()

OUTPUT_FILE = "products.csv"
NUM_RECORDS = 1000

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
    "Toys",
    "Food & Beverage",
    "Health & Beauty",
    "Automotive",
    "Office Supplies",
]

HEADERS = [
    "product_id",
    "product_name",
    "category",
    "price",
    "cost",
    "sku",
    "weight_kg",
    "stock_quantity",
    "supplier_id",
    "created_date",
]


def generate_products():
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            price = round(random.uniform(5.0, 500.0), 2)
            cost = round(price * random.uniform(0.3, 0.7), 2)
            writer.writerow(
                {
                    "product_id": i,
                    "product_name": fake.catch_phrase(),
                    "category": random.choice(CATEGORIES),
                    "price": price,
                    "cost": cost,
                    "sku": fake.bothify(text="???-#####").upper(),
                    "weight_kg": round(random.uniform(0.1, 25.0), 2),
                    "stock_quantity": random.randint(0, 500),
                    "supplier_id": random.randint(1, 1000),
                    "created_date": fake.date_between(
                        start_date="-2y", end_date="today"
                    ).isoformat(),
                }
            )
    print(f"Generated {NUM_RECORDS} product records in {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_products()
