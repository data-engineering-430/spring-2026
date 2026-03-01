import csv
import random
from faker import Faker

fake = Faker()

OUTPUT_FILE = "daily_sales.csv"
NUM_RECORDS = 1000

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "PayPal", "Apple Pay"]
CHANNELS = ["Online", "In-Store", "Phone", "Mobile App"]

HEADERS = [
    "sale_id",
    "sale_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "discount_pct",
    "payment_method",
    "channel",
    "region",
]


def generate_daily_sales():
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(5.0, 500.0), 2)
            discount = random.choice([0, 0, 0, 5, 10, 15, 20, 25])
            total = round(quantity * unit_price * (1 - discount / 100), 2)
            writer.writerow(
                {
                    "sale_id": i,
                    "sale_date": fake.date_between(
                        start_date="-1y", end_date="today"
                    ).isoformat(),
                    "customer_id": random.randint(1, 1000),
                    "product_id": random.randint(1, 1000),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_amount": total,
                    "discount_pct": discount,
                    "payment_method": random.choice(PAYMENT_METHODS),
                    "channel": random.choice(CHANNELS),
                    "region": fake.state_abbr(),
                }
            )
    print(f"Generated {NUM_RECORDS} daily sales records in {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_daily_sales()
