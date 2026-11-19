
from datetime import datetime
from pathlib import Path
import subprocess
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_DIR = Path("/opt/airflow/project")


def run_script(script_name):
    script_path = PROJECT_DIR / script_name

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_DIR),
        check=True
    )


with DAG(
    dag_id="stage2_csv_to_minio",
    description="Validate CSV, transform to partitioned Parquet, and upload to MinIO",
    start_date=datetime(2026, 11, 18),
    schedule=None,
    catchup=False,
    tags=["stage2", "csv", "parquet", "minio"],
) as dag:

    validate_csv = PythonOperator(
        task_id="validate_csv_schema",
        python_callable=run_script,
        op_args=["validate_schema.py"],
    )

    transform_csv = PythonOperator(
        task_id="transform_csv_to_parquet",
        python_callable=run_script,
        op_args=["transform_data.py"],
    )

    upload_minio = PythonOperator(
        task_id="upload_parquet_to_minio",
        python_callable=run_script,
        op_args=["upload_parquet_to_minio.py"],
    )

    validate_csv >> transform_csv >> upload_minio
