# Airflow DAGs to Aggregate COVID Data

This repo contains DAGs to get daily state-related COVID data from the [covidtracking.com API](https://covidtracking.com), push that data as a series of CSV files to Amazon S3, and then load those CSVs downstream into Snowflake tables using the [S3 to Snowflake Transfer Operator](https://airflow.readthedocs.io/en/latest/_api/airflow/providers/snowflake/operators/s3_to_snowflake/index.html).

These DAGs are mostly used for Airflow workshops and training sessions.

## Tools Used

- [S3Hook](https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html)
- [Hashicorp Vault as a Secrets Backend](https://www.astronomer.io/guides/airflow-and-hashicorp-vault/)
- [S3ToSnowflakeTransferOperator](https://airflow.readthedocs.io/en/latest/_api/airflow/providers/snowflake/operators/s3_to_snowflake/index.html)
- [PythonOperator](https://airflow.apache.org/docs/stable/howto/operator/python.html)
