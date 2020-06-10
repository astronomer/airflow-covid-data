from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks import S3Hook
from datetime import datetime, timedelta
import os
import requests
S3_CONN_ID = 'astro-s3-workshop'
BUCKET = 'astro-workshop-bucket'
name = 'covid_data'  # swap your name here

def upload_to_s3(endpoint, date):

    # Instanstiaute
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

    # Base URL
    url = 'https://covidtracking.com/api/v1/states/'

    res = requests.get(url+'{0}/{1}.csv'.format(endpoint, date))

    # Take string, upload to S3 using predefined method
    s3_hook.load_string(res.text, 'test_{0}.csv'.format(endpoint), bucket_name=BUCKET, replace=True)

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

endpoints = ['ca', 'co']
date = '{{ ds_nodash }}'

# Using a DAG context manager, you don't have to specify the dag property of each task

with DAG('s3_covid',
         start_date=datetime(2019, 1, 1),
         max_active_runs=1,
         # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
         schedule_interval='0 12 8-14,22-28 * 6',
         default_args=default_args,
         catchup=False  # enable if you don't want historical dag runs to run
         ) as dag:


    t0 = DummyOperator(task_id='start')

    for endpoint in endpoints:
        generate_files = PythonOperator(
            task_id='generate_file_{0}'.format(endpoint),  # task id is generated dynamically
            python_callable=upload_to_s3,
            op_kwargs={'endpoint': endpoint, 'date': date}
        )