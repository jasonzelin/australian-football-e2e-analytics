import io
import os
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
# from google.cloud.bigquery.client import Client
# import pandas_gbq

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
def setup_logging(log_dir: str) -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),          # also print to console
        ],
    )
    return logging.getLogger(__name__)

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
    Returns raw bytes so we can read it in-memory without touching disk.
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
    response = requests.get(full_url, headers=headers, timeout=timeout)
    response.raise_for_status()                           # raises on 4xx/5xx
    size_mb = len(response.content) / (1024)
    logger.info(f"Download complete — {size_mb:.1f} kB received")
    if json.loads(response.text)['errors'] != []:
        logger.error(f"API returned errors: {json.loads(response.text)['errors']}")

    # Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(f"{output_dir}/{target_folder}/{target_file}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(response.content)

    dataframe = pd.DataFrame(json.loads(response.content)['response'])
    logger.info(f"Loaded '{target_folder}/{target_file}' — {len(dataframe):,} rows, {len(dataframe.columns)} columns")

    return None

# ---------------------------------------------------------------------------
# STEP 2 — Inspect ZIP contents and extract target files
# ---------------------------------------------------------------------------
def extract_afl_data(
        data_bytes: bytes,
        output_dir: str,
        target_folder: str,
        target_file: str,
        logger: logging.Logger,
    ) -> pd.DataFrame:
    """
    Open the bytes file, then extract only the target files into pandas DataFrames.
    Returns a DataFrame.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"{target_folder} / {target_file}.json"
    output_file.write_bytes(data_bytes)

    dataframe = pd.DataFrame(json.loads(data_bytes)['response'])
    logger.info(f"Loaded '{target_file}' — {len(dataframe):,} rows, {len(dataframe.columns)} columns")

    return dataframe