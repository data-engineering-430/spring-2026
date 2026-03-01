# Project 1: Rapid ETL Pipeline Development

**Course Module:** Data Engineering Practicum
**Project Type:** Individual Sprint Project
**Duration:** 3 Weeks (15 Working Days)

---

## 1. Executive Summary

### 1.1 Overview

In this project you will build a functional ETL (Extract, Transform, Load) pipeline that processes customer, product, and order data from CSV, JSON, and YAML files into a PostgreSQL database. This simulates a real-world proof-of-concept (POC) project where a data engineer must deliver a working pipeline under tight deadlines.

You will choose **one** of two orchestration tools to build your pipeline:

- **Option A: Apache Airflow** -- a Python-based workflow orchestration platform
- **Option B: Apache NiFi** -- a flow-based data integration platform

Both options carry equal weight and are graded against the same acceptance criteria. Choose the tool that best fits your learning goals.

### 1.2 Sprint Goals

- Deliver a working ETL pipeline within a 3-week timeline
- Demonstrate proficiency with your chosen orchestration tool (Airflow or NiFi)
- Show ability to handle multiple data formats (CSV, JSON, YAML)
- Practice structured, deadline-driven development as an individual contributor

---

## 2. Core Requirements (MVP)

### 2.1 Data Generation

Use the **Python Faker library** to generate synthetic data. Create **one script** (`generate_data.py`) that produces all data files in a single run.

#### Volume and Format

| Entity    | Records | Formats          | Files |
|-----------|---------|------------------|-------|
| Customers | 1,000   | CSV, JSON, YAML  | 3     |
| Products  | 1,000   | CSV, JSON, YAML  | 3     |
| Orders    | 1,000   | CSV, JSON, YAML  | 3     |
| **Total** | **3,000** | --             | **9** |

#### Customer Schema (Minimum 8 Fields)

| Field              | Type    | Constraints         |
|--------------------|---------|---------------------|
| customer_id        | integer | unique              |
| first_name         | string  |                     |
| last_name          | string  |                     |
| email              | string  | unique              |
| phone              | string  |                     |
| city               | string  |                     |
| registration_date  | date    |                     |
| customer_type      | string  | Regular/Premium/VIP |

#### Product Schema (Minimum 7 Fields)

| Field          | Type    | Constraints |
|----------------|---------|-------------|
| product_id     | integer | unique      |
| product_name   | string  |             |
| category       | string  |             |
| brand          | string  |             |
| unit_price     | decimal |             |
| stock_quantity | integer |             |
| is_active      | boolean |             |

#### Order Schema (Minimum 8 Fields)

| Field          | Type      | Constraints                     |
|----------------|-----------|---------------------------------|
| order_id       | integer   | unique                          |
| customer_id    | integer   | foreign key to customers        |
| order_date     | timestamp |                                 |
| order_status   | string    | Pending/Shipped/Delivered       |
| payment_method | string    |                                 |
| total_amount   | decimal   |                                 |
| discount_amount| decimal   |                                 |
| shipping_cost  | decimal   |                                 |

#### Data Generation Rules

- Ensure **referential integrity**: every `customer_id` in orders must reference a valid customer
- Use Faker providers appropriate to each field (e.g., `fake.email()`, `fake.city()`)
- All 9 files must be generated from a single script execution

---

### 2.2 Pipeline Requirements

Choose **one** of the two options below. Both are equivalent in scope and grading weight.

#### Option A: Apache Airflow

##### DAG Structure

Create **one main DAG** (`etl_pipeline.py`) with the following task structure:

```
file_validation >> database_setup >> [extract_csv, extract_json, extract_yaml] >> load_customers >> load_products >> load_orders >> data_validation >> completion
```

##### Task Definitions

| Task               | Description                                          | Dependencies            |
|--------------------|------------------------------------------------------|-------------------------|
| file_validation    | Check that all 9 data files exist and are readable   | None (start)            |
| database_setup     | Create tables if not exist, clear staging data       | file_validation         |
| extract_csv        | Read and parse all CSV files                         | database_setup          |
| extract_json       | Read and parse all JSON files                        | database_setup          |
| extract_yaml       | Read and parse all YAML files                        | database_setup          |
| load_customers     | Insert customer records into PostgreSQL              | extract_csv, extract_json, extract_yaml |
| load_products      | Insert product records into PostgreSQL               | extract_csv, extract_json, extract_yaml |
| load_orders        | Insert order records into PostgreSQL                 | load_customers (foreign key dependency) |
| data_validation    | Verify row counts and foreign key relationships      | load_orders             |
| completion         | Log pipeline success and archive processed files     | data_validation         |

##### Scheduling

- Schedule the DAG to run **daily** at a fixed time
- Support **manual triggering** via the Airflow UI
- No complex scheduling patterns required

##### Technical Notes

- Use Airflow's **built-in operators** (PythonOperator, BashOperator, etc.)
- You may **hardcode configuration values** for demo purposes
- Use **pandas** for all file reading and data processing
- Airflow version 2.0 or later

##### Recommended File Layout

```
project/
  dags/
    etl_pipeline.py       # Main DAG file
  scripts/
    generate_data.py      # Faker data generation
  sql/
    schema.sql            # Table DDL
  data/                   # Generated data files (9 files)
  docs/                   # Documentation
  docker-compose.yml      # Airflow + PostgreSQL services
  requirements.txt
  README.md
```

---

#### Option B: Apache NiFi

##### Flow Structure

Create **one processor group** named `ETL_Pipeline` containing the following logical stages:

```
File Validation >> Database Setup >> [CSV Extraction, JSON Extraction, YAML Extraction] >> Customer Loading >> Product Loading >> Order Loading >> Data Validation >> Completion
```

##### Processor Group Layout

Organize processors into labeled sub-groups within the main `ETL_Pipeline` group:

| Stage                | Processors                                                  | Connections              |
|----------------------|-------------------------------------------------------------|--------------------------|
| File Validation      | ListFile, RouteOnAttribute (check 9 files exist)            | None (start)             |
| Database Setup       | ExecuteSQL (CREATE TABLE IF NOT EXISTS, clear staging)       | File Validation          |
| CSV Extraction       | GetFile, ConvertRecord (CSVReader to output)                 | Database Setup           |
| JSON Extraction      | GetFile, ConvertRecord (JsonTreeReader to output)            | Database Setup           |
| YAML Extraction      | GetFile, ExecuteScript (parse YAML to JSON/Avro)            | Database Setup           |
| Customer Loading     | PutDatabaseRecord or ConvertRecord + PutSQL (insert customers) | All Extraction stages  |
| Product Loading      | PutDatabaseRecord or ConvertRecord + PutSQL (insert products)  | All Extraction stages  |
| Order Loading        | PutDatabaseRecord or ConvertRecord + PutSQL (insert orders)    | Customer Loading (foreign key dependency) |
| Data Validation      | ExecuteSQL (row counts), RouteOnAttribute (verify counts)      | Order Loading          |
| Completion           | ExecuteScript (log success), MoveFile (archive files)          | Data Validation        |

##### Controller Services

Configure the following controller services at the root or processor group level:

| Service                     | Purpose                                  |
|-----------------------------|------------------------------------------|
| DBCPConnectionPool          | PostgreSQL JDBC connection               |
| CSVReader                   | Parse CSV files with header              |
| JsonTreeReader              | Parse JSON files                         |
| AvroRecordSetWriter (or JsonRecordSetWriter) | Standardize output format  |

##### Scheduling

- Set the **ListFile** processor to run on a **timer-driven schedule** (e.g., every 24 hours)
- Support **manual execution** by starting/stopping the processor group
- Use **CRON-driven scheduling** as an alternative if preferred

##### Technical Notes

- Use NiFi version 1.x or 2.x
- For YAML parsing, use an **ExecuteScript** processor (Groovy or Python) since NiFi does not have a native YAML reader
- Use **PutDatabaseRecord** for bulk inserts where possible for better performance
- You may use the **NiFi Registry** for version control of flows, but it is not required
- Connection strings and credentials may be **hardcoded in controller services** for demo purposes

##### Recommended File Layout

```
project/
  scripts/
    generate_data.py      # Faker data generation
  sql/
    schema.sql            # Table DDL
  nifi/
    flow-template.xml     # Exported NiFi flow template (or flow.json for NiFi 2.x)
  data/                   # Generated data files (9 files)
  docs/                   # Documentation
  docker-compose.yml      # NiFi + PostgreSQL services
  requirements.txt        # Python dependencies (for data generation)
  README.md
```

---

### 2.3 Database Requirements

#### PostgreSQL Setup

- PostgreSQL version **12 or later**
- Single database with the **public** schema
- Basic table structure (no partitioning required)

#### Table Definitions

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(50),
    registration_date DATE,
    customer_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    brand VARCHAR(50),
    unit_price DECIMAL(10,2),
    stock_quantity INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP,
    order_status VARCHAR(20),
    payment_method VARCHAR(30),
    total_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE etl_audit (
    run_id SERIAL PRIMARY KEY,
    dag_name VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20),
    records_processed INTEGER
);
```

**Notes:**

- Each main table includes an automatic `created_at` timestamp
- The `etl_audit` table tracks pipeline run metadata (use `dag_name` for Airflow DAG name or NiFi processor group name)
- Orders reference customers via foreign key -- customers must be loaded first

---

### 2.4 Error Handling

Implement basic error handling throughout your pipeline:

- **File operations:** Try-catch blocks around all file reads; fail gracefully if a file is missing or corrupted
- **Database operations:** Handle connection errors, constraint violations (duplicate keys, foreign key failures), and transaction rollbacks
- **Logging:** Write errors to console output and/or a log file with timestamps
- **Pipeline-level:** Record success or failure status in the `etl_audit` table after each run
- **Email notification on failure:** Optional (nice-to-have)

---

## 3. Individual Project Responsibilities

As an individual project, you are responsible for all aspects of the pipeline. The work maps to three areas that were originally divided among team members:

| Area                          | Responsibilities                                                                                 |
|-------------------------------|--------------------------------------------------------------------------------------------------|
| Database and Backend          | Set up PostgreSQL, create tables and schema, write data loading functions, test database operations |
| Pipeline Orchestration        | Install and configure Airflow or NiFi, develop the pipeline flow, implement task/processor dependencies, handle scheduling |
| Data Generation and Testing   | Create the Faker data generation script, generate all 9 data files, write basic validation checks, prepare documentation |

You should plan your time across all three areas.

---

## 4. Deliverables

### 4.1 Code Deliverables

#### For Option A (Airflow)

| File                | Description                                      |
|---------------------|--------------------------------------------------|
| `generate_data.py`  | Faker script that generates all 9 data files     |
| `etl_pipeline.py`   | Main Airflow DAG with all tasks defined           |
| `schema.sql`        | Table creation DDL and sample queries             |
| `requirements.txt`  | Python dependencies                               |
| `airflow.cfg`       | Airflow configuration (if modified from defaults) |
| `docker-compose.yml` | Docker Compose service definitions                |
| `.env`              | Environment variables (credentials) -- do not commit to public repos |

#### For Option B (NiFi)

| File                      | Description                                      |
|---------------------------|--------------------------------------------------|
| `generate_data.py`        | Faker script that generates all 9 data files     |
| `flow-template.xml` (or `flow.json`) | Exported NiFi flow template            |
| `schema.sql`              | Table creation DDL and sample queries             |
| `requirements.txt`        | Python dependencies (for data generation)         |
| `docker-compose.yml`      | Docker Compose service definitions                |
| `.env`                    | Environment variables (credentials) -- do not commit to public repos |

### 4.2 Documentation Deliverables

| Document                          | Length    | Contents                                                                      |
|-----------------------------------|-----------|-------------------------------------------------------------------------------|
| README.md                         | 2--3 pages | Project overview, setup instructions, how to run the pipeline                 |
| Technical Documentation           | 5--7 pages | Architecture diagram, database schema diagram, data flow explanation, key design decisions |
| User Guide                        | 3--4 pages | Step-by-step installation, running the pipeline, troubleshooting common issues |

### 4.3 Presentation and Demo

- **Presentation:** 10 minutes covering project architecture, design decisions, and lessons learned
- **Live Demo:** 5 minutes showing the pipeline running end-to-end
- **Q&A:** 5 minutes
- **Backup Video Recording:** 5--10 minutes showing the pipeline running end-to-end with brief architecture explanation (serves as backup if the live demo encounters issues)

---

## 5. Technical Constraints

| Constraint             | Requirement                                        |
|------------------------|----------------------------------------------------|
| Python                 | 3.8 or later                                       |
| Apache Airflow         | 2.0 or later (Option A only)                       |
| Apache NiFi            | 1.x or 2.x (Option B only)                         |
| PostgreSQL             | 12 or later                                        |
| Faker                  | Latest version                                     |
| Pandas                 | For data processing (both options)                 |
| Git                    | Required for version control                       |
| Docker                 | Required (see Section 5.1)                         |

### 5.1 Docker (Required)

The entire project must run inside Docker containers using `docker compose`. This ensures a reproducible environment and is a core grading requirement.

- Use `docker compose` to define all services (PostgreSQL, Airflow or NiFi, and any supporting services)
- Provide a `docker-compose.yml` (or `compose.yml`) in the project root
- The pipeline must be launchable with a single `docker compose up` command (after data generation)
- Include Docker setup instructions in your README
- Use volume mounts to share data files and configuration between the host and containers
- Use environment variables (via `.env` file) for credentials and configuration -- do not hardcode secrets in `docker-compose.yml`

---

## 6. Acceptance Criteria

### 6.1 Must-Have (Minimum for Passing)

- [ ] Faker script generates exactly 1,000 records per entity
- [ ] All 9 data files are created (3 entities x 3 formats)
- [ ] Pipeline (Airflow DAG or NiFi flow) runs without errors
- [ ] Data is loaded into PostgreSQL with correct schema
- [ ] Foreign key relationships are maintained (orders reference valid customers)
- [ ] All services run in Docker containers via `docker compose`
- [ ] Basic documentation exists (README with setup and run instructions)
- [ ] Code is committed to a Git repository

### 6.2 Should-Have (Expected for Full Credit)

All Must-Have items, plus:

- [ ] Error handling is implemented (try-catch, transaction rollbacks)
- [ ] Logging is added to the pipeline (timestamped messages)
- [ ] Data validation checks run as part of the pipeline (row counts, referential integrity)
- [ ] Clear and complete documentation (all three documents)
- [ ] Successful live demo during presentation

### 6.3 Nice-to-Have (Bonus)

All Should-Have items, plus:

- [ ] Automated testing (unit tests for data generation, integration tests for pipeline)
- [ ] Performance optimization (bulk inserts, parallel processing)
- [ ] Monitoring dashboard (Airflow UI metrics or NiFi provenance/bulletin board)
- [ ] Professional presentation with polished slides

---

## 7. Resources and Support

### General

- **Python Faker Documentation:** [https://faker.readthedocs.io/](https://faker.readthedocs.io/)
- **PostgreSQL Documentation:** [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
- **Pandas Documentation:** [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)

### Option A: Apache Airflow

- **Airflow Documentation:** [https://airflow.apache.org/docs/](https://airflow.apache.org/docs/)
- **Airflow Tutorial:** [https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html)

### Option B: Apache NiFi

- **NiFi Documentation:** [https://nifi.apache.org/docs.html](https://nifi.apache.org/docs.html)
- **NiFi Getting Started Guide:** [https://nifi.apache.org/docs/nifi-docs/html/getting-started.html](https://nifi.apache.org/docs/nifi-docs/html/getting-started.html)
- **NiFi Expression Language Guide:** [https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html](https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html)

### Support

- Office hours and lab sessions as scheduled by the instructor
- Use the course discussion forum for technical questions
- Consult official documentation before asking for help

---

## 8. Submission Guidelines

### 8.1 GitHub Repository

Your repository must contain:

```
project-root/
  data/                 # Generated data files (9 files)
  docs/                 # Technical documentation, user guide
  docker-compose.yml    # Docker Compose service definitions
  README.md             # Project overview, setup, how to run
  requirements.txt      # Python dependencies
  schema.sql            # Database DDL
  generate_data.py      # Data generation script
  .env.example          # Template for environment variables (no real credentials)
  .gitignore            # Exclude .env, __pycache__, etc.

  # Option A only:
  dags/
    etl_pipeline.py     # Airflow DAG

  # Option B only:
  nifi/
    flow-template.xml   # Exported NiFi template (or flow.json)
```

**Important:** Do not commit `.env` files containing real credentials. Provide a `.env.example` with placeholder values instead.

### 8.2 Video Recording

- **Length:** 5--10 minutes
- **Content:** Show the pipeline running end-to-end with a brief explanation of the architecture
- **Purpose:** Serves as backup for the live demo
- **Format:** Upload to a streaming platform or submit as a file per instructor guidelines

### 8.3 Submission Checklist

Verify the following before submitting:

- [ ] All code committed and pushed to Git repository
- [ ] `docker compose up` launches all services successfully
- [ ] Pipeline runs end-to-end inside Docker containers
- [ ] All 9 data files present in `data/` directory
- [ ] Documentation complete (README, technical docs, user guide)
- [ ] `.env.example` provided (no real credentials committed)
- [ ] Presentation slides ready
- [ ] Demo video recorded and submitted
