import dotenv
import os
from pathlib import Path

from utils import \
    logger as app_logger, \
    data_extraction, \
    gemini_ai, \
    bigquery_load

import config

dotenv.load_dotenv()
afl_api_key = os.getenv("AFL_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Main Function
def main():
    logger = app_logger.setup_logging(config.LOG_DIR)
    
    # 1. Download
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

    # 2. Extract
    data_extraction.extract_afl_data(
        raw_data_dir=config.RAW_OUTPUT_DIR,
        output_dir=config.INTERMEDIATE_OUTPUT_DIR,
        logger=logger,
    )

    # 3. Data schema verification (using Gemini Gen AI)
    intermediate_data_dir = config.INTERMEDIATE_OUTPUT_DIR
    intermediate_data_list = Path(intermediate_data_dir).iterdir()
    for i in intermediate_data_list:
        schema_verif_result = gemini_ai.gemini_schema_verify(
            data_dir=f"{intermediate_data_dir}/{i.name}",
            project_id=os.getenv("GCP_PROJECT_ID"), # type: ignore # used  to suppress mypy error about Optional[str] vs str
            location=os.getenv("GCP_LOCATION") # type: ignore # used  to suppress mypy error about Optional[str] vs str
        )

        gemini_ai.store_schema_verification(
            schema_verif_result=schema_verif_result,
            output_dir=config.SCHEMA_VERIF_OUTPUT_DIR,
            file_name=i.name,
            logger=logger
        )

    # 4. Upload raw data and schema verification results to BigQuery Data Warehouse
    bigquery_load.bronze_ingest_to_bigquery(
        data_dir=config.INTERMEDIATE_OUTPUT_DIR,
        logger=logger
    )

    bigquery_load.schema_verif_ingest_to_bigquery(
        data_dir=config.SCHEMA_VERIF_OUTPUT_DIR,
        logger=logger
    )

if __name__ == "__main__":
    main()