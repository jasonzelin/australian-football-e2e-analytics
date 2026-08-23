import os
import logging
from datetime import datetime
from pathlib import Path
import re

import pandas as pd
from google.cloud.bigquery.client import Client
import pandas_gbq

def bronze_ingest_to_bigquery(
    data_dir: str,
    bigquery_schema_name:str,
    ingestion_type: str,
    logger: logging.Logger,
) -> None:
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account_key.json'
    client = Client()

    data_files = list(Path(data_dir).iterdir())

    logger.info(f"Starting ingestion to BigQuery for files in local directory {data_dir}...")
    logger.info("-" * 55)

    for i in data_files:
        dataframe = pd.read_csv(i)
        table_id = f"{client.project}.{bigquery_schema_name}.{re.sub(r'\..*', '', i.name)}"
        
        logger.info(f"Starting uploading table {table_id} to BigQuery...")
        pandas_gbq.to_gbq(
            dataframe=dataframe,
            destination_table=table_id,
            if_exists=ingestion_type,
            bigquery_client=client
        )
        logger.info(f"Data successfully ingested into BigQuery table: {table_id}!")
    logger.info("-" * 55)
    logger.info(f"All tables in local directory {data_dir} successfully ingested into BigQuery. Ingestion complete ✓")
    logger.info("=" * 55)