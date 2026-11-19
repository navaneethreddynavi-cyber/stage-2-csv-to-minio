
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "dags" / "extraction" / "sample.csv"
OUTPUT_DIR = BASE_DIR / "output" / "parquet"


def transform_data():
    # Read source CSV
    df = pd.read_csv(CSV_PATH)

    # Convert timestamp to UTC datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="raise",
        utc=True,
        format="mixed"
    )

    # Convert satisfaction to numeric
    df["customer_satisfaction"] = pd.to_numeric(
        df["customer_satisfaction"],
        errors="raise"
    )

    # Create date partition column
    df["event_date"] = df["timestamp"].dt.strftime("%Y-%m-%d")

    # Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)

    # Write partitioned Parquet files
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        OUTPUT_DIR,
        engine="pyarrow",
        index=False,
        partition_cols=["event_date"]
    )

    print("TRANSFORMATION COMPLETED")
    print(f"Rows before deduplication: {before}")
    print(f"Duplicate rows removed: {removed}")
    print(f"Rows after deduplication: {len(df)}")
    print(f"Parquet output: {OUTPUT_DIR}")


if __name__ == "__main__":
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
