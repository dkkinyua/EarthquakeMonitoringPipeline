from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'deecodes',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

@dag(dag_id='test_dag', default_args=default_args, start_date=datetime(2025, 7, 11), schedule_interval='@hourly')
def test_dag():
    @task
    def say_hello():
        print("Airflow is working perfectly!")

    say_hello()

our_test = test_dag()