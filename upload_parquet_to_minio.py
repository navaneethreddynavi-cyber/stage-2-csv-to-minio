import os
from pathlib import Path
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

bucket_name = os.getenv("MINIO_BUCKET", "customer-care-data")
parquet_dir = Path("output/parquet")

for file_path in parquet_dir.rglob("*.parquet"):
    object_name = f"customer_care_emails/{file_path.parent.name}/{file_path.name}"

    client.fput_object(
        bucket_name,
        object_name,
        str(file_path)
    )

    print(f"Uploaded: {object_name}")

print("PARQUET UPLOAD COMPLETED")