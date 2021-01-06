from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import os
import requests
S3_CONN_ID = 'astro-s3-workshop'
BUCKET = 'astro-workshop-bucket'

def upload_to_s3(endpoint, date):

    # Instanstiaute
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
    print("Created Connection")
    print(s3_hook.get_session())
    print(s3_hook)

    # Base URL
    url = 'https://covidtracking.com/api/v1/states/'

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

endpoints = ['ca', 'co', 'ny', 'pa']
date = '{{ ds_nodash }}'
email_to = ['viraj@astronomer.io']

# Using a DAG context manager, you don't have to specify the dag property of each task

with DAG('covid_data_to_s3',
         start_date=datetime(2019, 1, 1),
         max_active_runs=1,
         # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False  # enable if you don't want historical dag runs to run
         ) as dag:


    t0 = DummyOperator(task_id='start')

    send_email = EmailOperator(
        task_id='send_email',
        to=email_to,
        subject='Covid to S3 DAG',
        html_content='<p>The Covid to S3 DAG completed successfully. Files can now be found on S3. <p>'
    )

    with TaskGroup('covid_task_group') as covid_group:
        for endpoint in endpoints:
            generate_files = PythonOperator(
                task_id='generate_file_{0}'.format(endpoint),
                python_callable=upload_to_s3,
                op_kwargs={'endpoint': endpoint, 'date': date}
            )
        
    t0 >> covid_group >> send_email