import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

airflow_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if airflow_path not in sys.path:
    sys.path.append(airflow_path)
from scripts.script import etl_process

load_dotenv()
default_args = {
    'owner': 'deecodes',
    'depend_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': [os.getenv("SENDER")],
    'email_on_failure': True,
    'email_on_retry': False
}

with DAG(
    dag_id='etl_process_dag',
    default_args=default_args,
    start_date=datetime(2025, 7, 11),
    schedule_interval='@hourly',
    catchup=False
) as dag:
    # etl process \
    task_1 = PythonOperator(
        task_id="ingestion",
        python_callable=etl_process
    )

    # sends email that ETL process is complete.
    task_2 = EmailOperator(
        task_id='send_confirmation_email',
        to=os.getenv("RECEIPIENT"),
        subject='DAG Run complete',
        html_content="ETL Pipeline DAG Run complete, check it out"
    )

    task_1 >> task_2
