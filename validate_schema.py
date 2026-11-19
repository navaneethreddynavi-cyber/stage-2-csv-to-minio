from pathlib import Path

import pandas as pd
import yaml


# Project paths
BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "dags" / "extraction" / "sample.csv"
CONTRACT_PATH = BASE_DIR / "customer_care_emails" / "schema_contract.yaml"


def validate_contract():
    # 1. Load the schema contract
    with open(CONTRACT_PATH, "r", encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    expected_columns = contract["columns"]

    # 2. Read the CSV
    df = pd.read_csv(CSV_PATH)

    errors = []

    # 3. Check missing and unexpected columns
    actual_columns = set(df.columns)
    required_columns = set(expected_columns.keys())

    missing_columns = required_columns - actual_columns
    unexpected_columns = actual_columns - required_columns

    if missing_columns:
        errors.append(f"Missing columns: {sorted(missing_columns)}")

    if contract.get("strict_columns", False) and unexpected_columns:
        errors.append(f"Unexpected columns: {sorted(unexpected_columns)}")

    # 4. Validate each column
    for column, rules in expected_columns.items():

        if column not in df.columns:
            continue

        series = df[column]
        expected_type = rules["type"]

        # Check nullability
        if not rules.get("nullable", True) and series.isnull().any():
            errors.append(f"{column}: null values are not allowed")

        # Check data type
        if expected_type == "string":
            invalid = series.dropna().map(
                lambda value: not isinstance(value, str)
            )

            if invalid.any():
                errors.append(f"{column}: expected string values")

        elif expected_type == "timestamp":
            converted = pd.to_datetime(
                series,
                errors="coerce",
                utc=True,
                format="mixed"
            )

            invalid = series.notna() & converted.isna()

            if invalid.any():
                errors.append(f"{column}: contains invalid timestamps")

        elif expected_type == "float":
            converted = pd.to_numeric(series, errors="coerce")

            invalid = series.notna() & converted.isna()

            if invalid.any():
                errors.append(f"{column}: expected numeric values")

        else:
            errors.append(
                f"{column}: unsupported contract type '{expected_type}'"
            )

    # 5. Fail if any validation rule is violated
    if errors:
        raise ValueError(
            "SCHEMA CONTRACT VALIDATION FAILED:\n- "
            + "\n- ".join(errors)
        )

    print("SCHEMA CONTRACT VALIDATION PASSED")
    print(f"Dataset: {contract['dataset_name']}")
    print(f"Rows validated: {len(df)}")
    print(f"Columns validated: {len(expected_columns)}")


if __name__ == "__main__":
    validate_contract()