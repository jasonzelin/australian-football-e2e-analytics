from utils import logger
import json
import logging
from datetime import datetime
import time
from pathlib import Path
import re

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# STEP 1 — Download the AFL data as JSON
# ---------------------------------------------------------------------------
def download_afl_data(
        url: str,
        url_params: dict | None,
        endpoint: str,
        api_key: str,
        timeout: int,
        output_dir: str,
        target_folder:str,
        target_file:str,
        logger: logging.Logger
    ) -> None:
    """
    Download the AFL data as JSON from the specified URL.
    """
    payload={}
    headers = {
        'x-apisports-key': api_key,
    }
    if url_params != 'N/A':
        full_url = f"{url}/{endpoint}?{'&'.join([f'{k}={v}' for k, v in url_params.items()])}" # type: ignore
    else:
        full_url = f"{url}/{endpoint}"

    logger.info(f"Downloading raw data from: {full_url}")
    logger.info("-" * 55)
    response = requests.get(full_url, headers=headers, timeout=timeout)
    response.raise_for_status() # raises on 4xx/5xx
    if re.search(r'rateLimit', str(json.loads(response.text)['errors'])):
        logger.error(f"API returned errors: {json.loads(response.text)['errors']}")
        logger.info("-" * 55)

        logger.info("Waiting for 60 seconds before retrying...")
        logger.info("-" * 55)
        time.sleep(60)  # wait 60 seconds before retrying

        response = requests.get(full_url, headers=headers, timeout=timeout)
        response.raise_for_status() # raises on 4xx/5xx

    elif json.loads(response.text)['errors'] != []:
        logger.error(f"API returned errors: {json.loads(response.text)['errors']}")
        logger.info("-" * 55)

    else:
        size_mb = len(response.content) / (1024)
        logger.info(f"Download complete — {size_mb:.1f} kB received")
        logger.info("-" * 55)

        output_file = Path(f"{output_dir}/{target_folder}/{target_file}.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(response.content)

        dataframe = pd.DataFrame(json.loads(response.content)['response'])
        logger.info(f"Loaded '{target_folder}/{target_file}' — {len(dataframe):,} rows, {len(dataframe.columns)} columns")

    return None

# ---------------------------------------------------------------------------
# STEP 2 — Combine raw data files per endpoint into one CSV file
# ---------------------------------------------------------------------------
def extract_afl_data(
        raw_data_dir: str,
        output_dir: str,
        logger: logging.Logger,
    ) -> None:
    """
    Open the bytes file, then extract only the target files into pandas DataFrames.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    raw_bytes_folders = list(Path(raw_data_dir).iterdir())

    for r in raw_bytes_folders:
        logger.info(f"Extracting data from {r.name}")
        raw_bytes_files = list(r.iterdir())
        df = pd.DataFrame()

        for f in raw_bytes_files:
            df_loop = pd.DataFrame(json.loads(f.read_bytes())['response'])
            df = pd.concat([df, df_loop], ignore_index=True) # type: ignore

        df.to_csv(Path(f"{output_dir}/{r.name}.csv"), index=False)
        logger.info(f"Loaded '{r}' — {len(df):,} rows, {len(df.columns)} columns")

    return None