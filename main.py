import dotenv
import os

from utils import logger as app_logger, data_extraction
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

if __name__ == "__main__":
    main()