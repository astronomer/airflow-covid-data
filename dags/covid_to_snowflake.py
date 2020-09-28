from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
from plugins.operators.s3_to_snowflake_operator import S3ToSnowflakeTransferOperator
from airflow.hooks import S3Hook
from datetime import datetime, timedelta
import os
import requests
S3_CONN_ID = 'astro-s3-workshop'
BUCKET = 'astro-workshop-bucket'
name = 'covid_data'  # swap your name here

def upload_to_s3(endpoint, date):
    print("called function")
    # Instanstiaute
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

    # Base URL

    url = 'https://covidtracking.com/api/v1/states/'
    # Grab data

    print(date)
    

    res = requests.get(url+'{0}/{1}.csv'.format(endpoint, date))
    # Take string, upload to S3 using predefined method
    s3_hook.load_string(res.text, '{0}_{1}.csv'.format(endpoint, date), bucket_name=BUCKET, replace=True)

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
# Using a DAG context manager, you don't have to specify the dag property of each task

endpoints = ['ca', 'co', 'ny', 'pa', 'xx', 'tt']

date = '{{ ds_nodash }}'
with DAG('covid_data_s3_to_snowflake',
         start_date=datetime(2020, 6, 1),
         max_active_runs=3,
         # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
         schedule_interval='@daily',
         default_args=default_args,
         catchup=True  # enable if you don't want historical dag runs to run
         ) as dag:



    t0 = DummyOperator(task_id='start')

    

    for endpoint in endpoints:
        generate_files = PythonOperator(
            task_id='generate_file_{0}'.format(endpoint),  # task id is generated dynamically
            python_callable=upload_to_s3,
            op_kwargs={'endpoint': endpoint, 'date': date}
        )

        snowflake = S3ToSnowflakeTransferOperator(
        task_id='upload_{0}_snowflake'.format(endpoint),
        s3_keys=['{0}_{1}.csv'.format(endpoint, date)],
        stage='covid_stage',
        table='state_data',
        schema='COVID_DEMO.covid',
        file_format='covid_data_csv',
        snowflake_conn_id="snowflake",
    )
        # snowflake_query= SnowflakeOperator(...)

        t0 >> generate_files >> snowflake
