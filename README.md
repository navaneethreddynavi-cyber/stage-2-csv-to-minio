\# Stage 2: Local CSV to MinIO Parquet Pipeline



An Airflow pipeline that reads a customer-care emails CSV, validates it against a schema contract, transforms it, and loads it into MinIO as Parquet partitioned by `event\_date`. Airflow, Postgres and MinIO all run locally with Docker Compose.



\## Flow



```

dags/extraction/sample.csv

&#x20;       |

&#x20;       v

validate\_csv\_schema  ->  transform\_csv\_to\_parquet  ->  upload to MinIO

(fails on mismatch)      (dedupe, clean)               bucket: customer-care-data

&#x20;                        Parquet by event\_date         console: http://localhost:9001

```



\- The DAG is `stage2\_csv\_to\_minio` in `dags/pipelines/stage2\_csv\_to\_minio.py`.

\- The schema contract is `customer\_care\_emails/schema\_contract.yaml` and the dataset manifest is `customer\_care\_emails/manifest.yaml`.

\- If the CSV does not match the contract, `validate\_csv\_schema` fails and nothing is written to MinIO.

\- Output layout: `event\_date=YYYY-MM-DD/<file>.parquet`.



\## Project files



| File | Purpose |

|---|---|

| `docker-compose.yaml` | Airflow, Postgres and MinIO services |

| `Dockerfile.airflow` | Airflow image with pandas, pyarrow, minio, PyYAML, python-dotenv |

| `Dockerfile.minio` | MinIO image built from a local MinIO binary |

| `validate\_schema.py` | Checks the CSV against the schema contract |

| `transform\_data.py` | Cleans the data, removes duplicates, writes partitioned Parquet |

| `upload\_parquet\_to\_minio.py` | Uploads the Parquet files to the bucket |

| `test\_minio\_connection.py` | Quick MinIO connectivity check |

| `.env.example` | Template for credentials |



\## Prerequisites



\- Docker Desktop with Docker Compose

\- The dataset CSV placed at `dags/extraction/sample.csv` (not included in the repository because it holds customer data)

\- A MinIO server binary at `minio-source/minio` (not included because the file is about 147 MB, over GitHub's limit). `Dockerfile.minio` copies it into the image. If you use a different S3-compatible image, change the `minio` service in `docker-compose.yaml`.



\## Run steps



1\. Create your environment file and set your own credentials:

&#x20;  ```powershell

&#x20;  copy .env.example .env

&#x20;  ```

&#x20;  Edit `.env` and set `MINIO\_ROOT\_USER` and `MINIO\_ROOT\_PASSWORD`. Never commit `.env`.



2\. Build and start the stack:

&#x20;  ```powershell

&#x20;  docker compose up -d --build

&#x20;  ```

&#x20;  Airflow takes 2 to 3 minutes to start.



3\. Open Airflow at http://localhost:8081. The user is `admin`. Get the generated password with:

&#x20;  ```powershell

&#x20;  docker compose exec airflow cat /opt/airflow/standalone\_admin\_password.txt

&#x20;  ```



4\. Unpause and trigger the `stage2\_csv\_to\_minio` DAG. All three tasks should turn green.



5\. Open the MinIO console at http://localhost:9001, log in with the credentials from `.env`, and browse the `customer-care-data` bucket. You should see `event\_date=...` folders with Parquet files.



\## Testing the schema contract



`dags/extraction/sample\_invalid.csv` is a small file with a column removed. Point the DAG at it instead of `sample.csv`, trigger a run, and `validate\_csv\_schema` fails before anything is written to MinIO. Switch back to the valid CSV afterwards.



\## Ports



| Service | URL |

|---|---|

| Airflow UI | http://localhost:8081 |

| MinIO API | http://localhost:9000 |

| MinIO console | http://localhost:9001 |



\## Notes



\- This setup is for local development only. The Postgres password in `docker-compose.yaml` and Airflow standalone mode are not meant for production.

\- `transform\_data.py` ends with `os.\_exit(0)` to avoid a pyarrow shutdown crash (`terminate called without an active exception`) that made Airflow mark the task as failed even though the output was written.

\- Airflow's first start prints many Azure `SyntaxWarning` messages. They are harmless.

