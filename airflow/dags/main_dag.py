import logging

from datetime import datetime
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    'owner': 'data-team',
    'start_date': datetime(2026, 1, 1)
}

with DAG(
    'main_dag',
    default_args=default_args,
    schedule="0 22 * * *",
    catchup=False
) as dag:
    
    # Task 1: Run data transformation in Databricks
    transform_data = DatabricksSubmitRunOperator(
        task_id='transform_bigquery_data',
        databricks_conn_id='databricks_default',
        new_cluster={
            'spark_version': '14.3.x-scala2.12',
            'node_type_id': 'm6i.large',
            'num_workers': 2
        },
        notebook_task={
            'notebook_path': '/Workspace/Users/your_email/transform_notebook',
        }
    )

    def notify_success(**context):
        logger   = logging.getLogger(__name__)
        manifest = context["ti"].xcom_pull(key="manifest", task_ids="ingest_gtfs_data")

        logger.info("=" * 55)
        logger.info("PIPELINE RUN COMPLETE")
        logger.info(f"  DAG run ID : {context['run_id']}")
        logger.info(f"  Exec date  : {context['logical_date']}")
        if manifest:
            logger.info("  Tables loaded:")
            for table, meta in manifest["tables"].items():
                logger.info(f"    {table:<20} {meta['rows']:>8,} rows")
        logger.info("=" * 55)
    
    # Task 2: Post-processing (optional)
    notify_completion = PythonOperator(
        task_id='notify_completion',
        python_callable=notify_success
    )
    
    # -----------------------------------------------------------------------
    # Task dependencies — defines the execution order
    # -----------------------------------------------------------------------
    transform_data >> notify_completion # type: ignore 