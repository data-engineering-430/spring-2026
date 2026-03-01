"""
DAG: csv_to_json_yaml

Purpose:
    Reads a CSV file containing 10,000 fake student records, validates the data,
    then converts it into both JSON and YAML formats. Each step is a separate
    Airflow task so the pipeline is observable, restartable, and auditable.

Tasks:
    1. validate_csv   -- Checks that the source CSV file exists and is non-empty.
    2. csv_to_json    -- Reads the CSV and writes a JSON file.
    3. csv_to_yaml    -- Reads the CSV and writes a YAML file.
    4. report_summary -- Logs row counts and output file sizes as a final check.

Task dependency graph:
    validate_csv >> [csv_to_json, csv_to_yaml] >> report_summary
"""

import csv
import json
import os
from datetime import datetime, timedelta

import yaml
from airflow import DAG
from airflow.operators.python import PythonOperator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = "/opt/airflow/data"
CSV_FILE = os.path.join(DATA_DIR, "students.csv")
JSON_FILE = os.path.join(DATA_DIR, "students.json")
YAML_FILE = os.path.join(DATA_DIR, "students.yaml")

# ---------------------------------------------------------------------------
# Task functions
# ---------------------------------------------------------------------------


def validate_csv(**kwargs):
    """
    Verify that the source CSV file exists and contains data.

    This task runs first to fail fast if the input file is missing or empty,
    preventing downstream tasks from running on bad input.

    Pushes the row count to XCom so later tasks can reference it.
    """
    if not os.path.isfile(CSV_FILE):
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("CSV file is empty (no header row)")

        row_count = sum(1 for _ in reader)

    if row_count == 0:
        raise ValueError("CSV file has a header but no data rows")

    print(f"Validation passed: {row_count} data rows, {len(header)} columns")
    print(f"Columns: {header}")

    # Push row count to XCom for downstream tasks
    kwargs["ti"].xcom_push(key="row_count", value=row_count)
    kwargs["ti"].xcom_push(key="columns", value=header)


def convert_csv_to_json(**kwargs):
    """
    Read the CSV file and write the contents as a JSON array.

    Each row becomes a JSON object with keys taken from the CSV header.
    Numeric fields (student_id, gpa, enrollment_year, zip_code) are cast
    to their appropriate types so the JSON output uses numbers, not strings.
    """
    records = []

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Cast numeric fields to proper types
            row["student_id"] = int(row["student_id"])
            row["gpa"] = float(row["gpa"])
            row["enrollment_year"] = int(row["enrollment_year"])
            records.append(row)

    with open(JSON_FILE, "w") as f:
        json.dump(records, f, indent=2)

    file_size = os.path.getsize(JSON_FILE)
    print(f"Wrote {len(records)} records to {JSON_FILE} ({file_size:,} bytes)")


def convert_csv_to_yaml(**kwargs):
    """
    Read the CSV file and write the contents as a YAML document.

    The output is a YAML list of mappings. Like the JSON task, numeric
    fields are cast so the YAML output uses proper scalar types.
    """
    records = []

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["student_id"] = int(row["student_id"])
            row["gpa"] = float(row["gpa"])
            row["enrollment_year"] = int(row["enrollment_year"])
            records.append(row)

    with open(YAML_FILE, "w") as f:
        yaml.dump(records, f, default_flow_style=False, allow_unicode=True)

    file_size = os.path.getsize(YAML_FILE)
    print(f"Wrote {len(records)} records to {YAML_FILE} ({file_size:,} bytes)")


def report_summary(**kwargs):
    """
    Print a summary of the conversion results.

    Pulls the original row count from XCom and compares it against
    the records found in the generated JSON and YAML files. This acts
    as a simple data-integrity check.
    """
    ti = kwargs["ti"]
    original_count = ti.xcom_pull(task_ids="validate_csv", key="row_count")
    columns = ti.xcom_pull(task_ids="validate_csv", key="columns")

    # Count records in JSON output
    with open(JSON_FILE, "r") as f:
        json_records = json.load(f)
    json_count = len(json_records)

    # Count records in YAML output
    with open(YAML_FILE, "r") as f:
        yaml_records = yaml.safe_load(f)
    yaml_count = len(yaml_records)

    json_size = os.path.getsize(JSON_FILE)
    yaml_size = os.path.getsize(YAML_FILE)
    csv_size = os.path.getsize(CSV_FILE)

    print("=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Source CSV:    {original_count} rows, {len(columns)} columns, {csv_size:,} bytes")
    print(f"JSON output:  {json_count} records, {json_size:,} bytes")
    print(f"YAML output:  {yaml_count} records, {yaml_size:,} bytes")
    print(f"Columns:      {', '.join(columns)}")
    print("=" * 60)

    if json_count != original_count or yaml_count != original_count:
        raise ValueError(
            f"Record count mismatch! CSV={original_count}, "
            f"JSON={json_count}, YAML={yaml_count}"
        )

    print("All counts match. Conversion completed successfully.")


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="csv_to_json_yaml",
    default_args=default_args,
    description="Read a CSV of student records and convert to JSON and YAML",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["data-conversion", "csv", "class2"],
) as dag:

    validate = PythonOperator(
        task_id="validate_csv",
        python_callable=validate_csv,
    )

    to_json = PythonOperator(
        task_id="csv_to_json",
        python_callable=convert_csv_to_json,
    )

    to_yaml = PythonOperator(
        task_id="csv_to_yaml",
        python_callable=convert_csv_to_yaml,
    )

    summary = PythonOperator(
        task_id="report_summary",
        python_callable=report_summary,
    )

    # Task dependencies:
    #   validate_csv runs first
    #   csv_to_json and csv_to_yaml run in parallel after validation
    #   report_summary runs after both conversions complete
    validate >> [to_json, to_yaml] >> summary
