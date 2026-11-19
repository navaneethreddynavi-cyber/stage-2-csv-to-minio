import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

bucket_name = os.getenv("MINIO_BUCKET", "customer-care-data")

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print(f"Bucket created: {bucket_name}")
else:
    print(f"Bucket already exists: {bucket_name}")