import csv
from faker import Faker

fake = Faker()

OUTPUT_FILE = "customers.csv"
NUM_RECORDS = 1000

HEADERS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "address",
    "city",
    "state",
    "zip_code",
    "date_of_birth",
    "registration_date",
]


def generate_customers():
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            writer.writerow(
                {
                    "customer_id": i,
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.email(),
                    "phone": fake.phone_number(),
                    "address": fake.street_address(),
                    "city": fake.city(),
                    "state": fake.state_abbr(),
                    "zip_code": fake.zipcode(),
                    "date_of_birth": fake.date_of_birth(
                        minimum_age=18, maximum_age=80
                    ).isoformat(),
                    "registration_date": fake.date_between(
                        start_date="-3y", end_date="today"
                    ).isoformat(),
                }
            )
    print(f"Generated {NUM_RECORDS} customer records in {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_customers()
