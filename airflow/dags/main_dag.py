import logging
from pathlib import Path
import os
import subprocess
import dotenv

from datetime import datetime
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.standard.operators.python import PythonOperator

from utils import \
    logger as app_logger, \
    data_extraction, \
    gemini_ai, \
    bigquery_load, \
    slack_notify

import config

dotenv.load_dotenv()
afl_api_key = os.getenv("AFL_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

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
    # -----------------------------------------------------------------------    
    # Task 1: Download data transformation from AFL endpoints
    # -----------------------------------------------------------------------
    def download_afl_data(**context):
        logger = app_logger.setup_logging(config.LOG_DIR)
        for e in config.ENDPOINTS.keys():
            logger.info("Starting AFL data ingestion")

            url_params = config.ENDPOINTS[e]
            if url_params == 'N/A':
                url_params = None
                data_extraction.download_afl_data(
                    url=f"{config.AFL_URL}",
                    url_params=config.ENDPOINTS[e],
                    endpoint=e,
                    timeout=config.REQUEST_TIMEOUT_SECONDS,
                    output_dir=config.RAW_OUTPUT_DIR,
                    target_folder=e,
                    target_file=e,
                    logger=logger,
                    api_key=afl_api_key # type: ignore # used  to suppress mypy error about Optional[str] vs str
                )
            else:
                for p in url_params:
                    data_extraction.download_afl_data(
                        url=f"{config.AFL_URL}",
                        url_params=p,
                        endpoint=e,
                        timeout=config.REQUEST_TIMEOUT_SECONDS,
                        output_dir=config.RAW_OUTPUT_DIR,
                        target_folder=e,
                        target_file='_'.join([f'{k}={v}' for k, v in p.items()]),
                        logger=logger,
                        api_key=afl_api_key # type: ignore # used  to suppress mypy error about Optional[str] vs str
                    )

    task_download_afl_data = PythonOperator(
        task_id='download_afl_data',
        python_callable=download_afl_data
    )

    # -----------------------------------------------------------------------    
    # Task 2: Extract data from raw files
    # -----------------------------------------------------------------------
    def extract_afl_data(**context):
        logger = app_logger.setup_logging(config.LOG_DIR)
        data_extraction.extract_afl_data(
                raw_data_dir=config.RAW_OUTPUT_DIR,
                output_dir=config.INTERMEDIATE_OUTPUT_DIR,
                logger=logger,
            )

    task_extract_afl_data = PythonOperator(
        task_id='extract_afl_data',
        python_callable=extract_afl_data
    )

    # -----------------------------------------------------------------------    
    # Task 3: Data schema verification (using Gemini Gen AI)
    # -----------------------------------------------------------------------
    # def verify_afl_data_schemas(**context):
    #     logger = app_logger.setup_logging(config.LOG_DIR)
    #     intermediate_data_dir = config.INTERMEDIATE_OUTPUT_DIR
    #     intermediate_data_list = Path(intermediate_data_dir).iterdir()
    #     for i in intermediate_data_list:
    #         schema_verif_result = gemini_ai.gemini_schema_verify(
    #             data_dir=f"{intermediate_data_dir}/{i.name}",
    #             project_id=os.getenv("GCP_PROJECT_ID"), # type: ignore # used  to suppress mypy error about Optional[str] vs str
    #             location=os.getenv("GCP_LOCATION") # type: ignore # used  to suppress mypy error about Optional[str] vs str
    #         )
    
    #         gemini_ai.store_schema_verification(
    #             schema_verif_result=schema_verif_result,
    #             output_dir=config.SCHEMA_VERIF_OUTPUT_DIR,
    #                 file_name=i.name,
    #                 logger=logger
    #             )

    # task_verify_afl_data_schemas = PythonOperator(
    #     task_id='verify_afl_data_schemas',
    #     python_callable=verify_afl_data_schemas
    # )

    # -----------------------------------------------------------------------    
    # Task 4: Sending notification if schema verification fails (below threshold)
    # -----------------------------------------------------------------------
    def send_below_threshold_notification(**context):
        logger = app_logger.setup_logging(config.LOG_DIR)
        logger.info("Running schema verification threshold check")

        slack_notify.send_slack_notification(
            schema_verif_dir=config.SCHEMA_VERIF_OUTPUT_DIR,
            minimum_global_confidence_threshold=config.MINIMUM_GLOBAL_CONFIDENCE_THRESHOLD,
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN"), # type: ignore # used  to suppress mypy error about Optional[str] vs str
            channel_id=config.SLACK_CHANNEL_ID, # type: ignore # used  to suppress
            logger=app_logger.setup_logging(config.LOG_DIR)
        )

    task_slack_notify = PythonOperator(
        task_id="slack_notify",
        python_callable=send_below_threshold_notification
    )

    # -----------------------------------------------------------------------    
    # Task 5: Load data to BigQuery
    # -----------------------------------------------------------------------
    def load_afl_data_to_bigquery(**context):
        logger = app_logger.setup_logging(config.LOG_DIR)
        bigquery_load.bronze_ingest_to_bigquery(
            data_dir=config.INTERMEDIATE_OUTPUT_DIR,
            logger=logger
        )
    
        # bigquery_load.schema_verif_ingest_to_bigquery(
        #     data_dir=config.SCHEMA_VERIF_OUTPUT_DIR,
        #     logger=logger
        # )

    task_load_afl_data_to_bigquery = PythonOperator(
        task_id='load_afl_data_to_bigquery',
        python_callable=load_afl_data_to_bigquery
    )

    # -----------------------------------------------------------------------    
    # Task 6: Transform data using dbt
    # -----------------------------------------------------------------------
    def run_dbt_models(**context):
        logger = logging.getLogger(__name__)
        logger.info(f"Running dbt from: {config.DBT_DIR}")

        result = subprocess.run(
            ["dbt", "run", "--target", "prod"],
            cwd=config.DBT_DIR,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "GCP_PROJECT_ID": os.environ.get("GCP_PROJECT_ID", ""),
                "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
            },
        )

        logger.info(result.stdout)

        if result.returncode != 0:
            logger.error(result.stderr)
            raise Exception(f"dbt run failed:\n{result.stderr}")

        logger.info("dbt run complete ✓")

    task_dbt_run = PythonOperator(
        task_id="dbt_run",
        python_callable=run_dbt_models
    )
    
    # -----------------------------------------------------------------------
    # Logging and notification task
    # -----------------------------------------------------------------------
    def notify_success(**context):
        logger   = logging.getLogger(__name__)
        manifest = context["ti"].xcom_pull(key="manifest", task_ids="extract_afl_data")

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
    task_download_afl_data >> task_extract_afl_data >> task_slack_notify >> task_load_afl_data_to_bigquery >> task_dbt_run >> notify_completion # type: ignore # used  to suppress mypy error about Optional[str] vs str