# data-gen

Synthetic data generator for DATA430. Produces realistic fake CSV datasets for customers, products, suppliers, and daily sales using the [Faker](https://faker.readthedocs.io/) library.

## Prerequisites

- Python 3.11 or later
- [Poetry](https://python-poetry.org/) (dependency manager)

## Setup

### macOS

1. Install Python (if not already installed):

```bash
brew install python@3.11
```

2. Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, add Poetry to your PATH by adding the following line to your `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
```

3. Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd data-gen
poetry install
```

### Windows

1. Install Python 3.11 or later from [python.org](https://www.python.org/downloads/). During installation, make sure to check **"Add Python to PATH"**.

2. Open **PowerShell** and install Poetry:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

After installation, add Poetry to your PATH. Add the following to your system environment variables or run:

```powershell
$env:PATH += ";$env:APPDATA\Python\Scripts"
```

To make this permanent, add `%APPDATA%\Python\Scripts` to your system PATH through **Settings > System > About > Advanced system settings > Environment Variables**.

3. Clone the repository and install dependencies:

```powershell
git clone <repository-url>
cd data-gen
poetry install
```

This installs the `faker` library and any other project dependencies defined in `pyproject.toml`.

## Running the Generators

Each generator script produces a CSV file with 1,000 records in the project root directory. Run them individually or all at once.

### Individual generators

```bash
poetry run python generate_customers.py
poetry run python generate_products.py
poetry run python generate_suppliers.py
poetry run python generate_daily_sales.py
```

### Run all generators at once

**macOS / Linux:**

```bash
poetry run python generate_customers.py && \
poetry run python generate_products.py && \
poetry run python generate_suppliers.py && \
poetry run python generate_daily_sales.py
```

**Windows (PowerShell):**

```powershell
poetry run python generate_customers.py; `
poetry run python generate_products.py; `
poetry run python generate_suppliers.py; `
poetry run python generate_daily_sales.py
```

## Generated Datasets

| Script | Output File | Records | Description |
|---|---|---|---|
| `generate_customers.py` | `customers.csv` | 1,000 | Customer profiles with name, email, phone, address, DOB, and registration date |
| `generate_products.py` | `products.csv` | 1,000 | Product catalog with name, category, price, cost, SKU, weight, stock, and supplier reference |
| `generate_suppliers.py` | `suppliers.csv` | 1,000 | Supplier directory with company info, contact details, industry, and rating |
| `generate_daily_sales.py` | `daily_sales.csv` | 1,000 | Sales transactions with customer/product references, quantity, pricing, discount, payment method, and channel |

### Schema Details

**customers.csv**

`customer_id`, `first_name`, `last_name`, `email`, `phone`, `address`, `city`, `state`, `zip_code`, `date_of_birth`, `registration_date`

**products.csv**

`product_id`, `product_name`, `category`, `price`, `cost`, `sku`, `weight_kg`, `stock_quantity`, `supplier_id`, `created_date`

- Categories: Electronics, Clothing, Home & Garden, Sports, Books, Toys, Food & Beverage, Health & Beauty, Automotive, Office Supplies
- `supplier_id` references `suppliers.csv`

**suppliers.csv**

`supplier_id`, `company_name`, `contact_name`, `email`, `phone`, `address`, `city`, `state`, `country`, `industry`, `rating`, `contract_start_date`

- Industries: Manufacturing, Wholesale, Distribution, Import/Export, Agriculture, Technology, Textiles, Chemicals, Packaging, Raw Materials
- Rating ranges from 1.0 to 5.0

**daily_sales.csv**

`sale_id`, `sale_date`, `customer_id`, `product_id`, `quantity`, `unit_price`, `total_amount`, `discount_pct`, `payment_method`, `channel`, `region`

- Payment methods: Credit Card, Debit Card, Cash, PayPal, Apple Pay
- Channels: Online, In-Store, Phone, Mobile App
- `customer_id` references `customers.csv`, `product_id` references `products.csv`

## Configuration

Each generator script has constants at the top of the file that can be adjusted:

- `NUM_RECORDS` -- number of rows to generate (default: 1000)
- `OUTPUT_FILE` -- output CSV filename
