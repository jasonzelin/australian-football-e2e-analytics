import dotenv
import os
from pathlib import Path
import json

import utils

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

def main():
    dataframes_dict = {}
    for e in CONFIG["endpoints"]:
        logger = utils.setup_logging(CONFIG["log_dir"])
        logger.info("Starting AFL data ingestion")

        # 1. Download
        zip_byte = utils.download_afl_data(
            url=f"{CONFIG["afl_url"]}/{e}",
            timeout=CONFIG["request_timeout_seconds"],
            logger=logger,
            api_key=api_key # type: ignore # used  to suppress mypy error about Optional[str] vs str
        )

        # 2. Extract
        dataframe = utils.extract_afl_data(
            data_bytes=zip_byte,
            output_dir=CONFIG["output_dir"],
            target_file=e,
            logger=logger,
        )

        dataframes_dict[e] = dataframe

if __name__ == "__main__":
    main()