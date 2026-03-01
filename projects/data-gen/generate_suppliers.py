import csv
import random
from faker import Faker

fake = Faker()

OUTPUT_FILE = "suppliers.csv"
NUM_RECORDS = 1000

INDUSTRIES = [
    "Manufacturing",
    "Wholesale",
    "Distribution",
    "Import/Export",
    "Agriculture",
    "Technology",
    "Textiles",
    "Chemicals",
    "Packaging",
    "Raw Materials",
]

HEADERS = [
    "supplier_id",
    "company_name",
    "contact_name",
    "email",
    "phone",
    "address",
    "city",
    "state",
    "country",
    "industry",
    "rating",
    "contract_start_date",
]


def generate_suppliers():
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            writer.writerow(
                {
                    "supplier_id": i,
                    "company_name": fake.company(),
                    "contact_name": fake.name(),
                    "email": fake.company_email(),
                    "phone": fake.phone_number(),
                    "address": fake.street_address(),
                    "city": fake.city(),
                    "state": fake.state_abbr(),
                    "country": fake.country(),
                    "industry": random.choice(INDUSTRIES),
                    "rating": round(random.uniform(1.0, 5.0), 1),
                    "contract_start_date": fake.date_between(
                        start_date="-5y", end_date="today"
                    ).isoformat(),
                }
            )
    print(f"Generated {NUM_RECORDS} supplier records in {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_suppliers()
