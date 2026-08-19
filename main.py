import dotenv
import os
from pathlib import Path
import json

import utils

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

dotenv.load_dotenv()
api_key = os.getenv("API_KEY")


# Load config from root directory
config_path = Path(__file__).parent / "config.json"

if not config_path.exists():
    raise FileNotFoundError(
        f"config.json not found at {config_path}. "
        "Create or copy json values to config.json and fill in your values."
    )

with open(config_path) as f:
    CONFIG = json.load(f)

# Main Function
def main():
    logger = utils.setup_logging(CONFIG["log_dir"])
    
    # 1. Download
    for e in CONFIG["endpoints"].keys():
        logger.info("Starting AFL data ingestion")

        url_params = CONFIG["endpoints"][e]
        if url_params == 'N/A':
            url_params = None
            zip_byte = utils.download_afl_data(
                url=f"{CONFIG["afl_url"]}",
                url_params=CONFIG["endpoints"][e],
                endpoint=e,
                timeout=CONFIG["request_timeout_seconds"],
                output_dir=CONFIG["raw_output_dir"],
                target_folder=e,
                target_file=e,
                logger=logger,
                api_key=api_key # type: ignore # used  to suppress mypy error about Optional[str] vs str
            )
        else:
            for p in url_params:
                zip_byte = utils.download_afl_data(
                    url=f"{CONFIG["afl_url"]}",
                    url_params=p,
                    endpoint=e,
                    timeout=CONFIG["request_timeout_seconds"],
                    output_dir=CONFIG["raw_output_dir"],
                    target_folder=e,
                    target_file='_'.join([f'{k}={v}' for k, v in p.items()]),
                    logger=logger,
                    api_key=api_key # type: ignore # used  to suppress mypy error about Optional[str] vs str
                )

    # 2. Extract
    utils.extract_afl_data(
        raw_data_dir=CONFIG["raw_output_dir"],
        output_dir=CONFIG["intermediate_output_dir"],
        logger=logger,
    )

if __name__ == "__main__":
    main()