import json
from pathlib import Path
import logging

import pandas as pd

from utils import logger as app_logger
import config

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

logger = app_logger.setup_logging(log_dir=config.LOG_DIR)

def gemini_schema_verify(
        data_dir: str,
        project_id: str,
        location: str
    ) -> dict:

    vertexai.init(project=project_id, location=location)
    data = Path(data_dir)

    logger.info(f"Verifying the schema of {data.name}...")
    
    """Calls Gemini Flash with structured output schema enforcement."""
    model = GenerativeModel(
        str(config.GEMINI_MODEL),
        system_instruction=config.GEMINI_SYSTEM_PROMPT
    )
    response = model.generate_content(
        f"RAW_DATA_SAMPLE:\n{data.read_bytes()[0:102]}",
        generation_config=config.GEMINI_GENERATION_CONFIG
    )
    return json.loads(response.text.replace('```','').replace('json','')) #type: ignore

def store_schema_verification(
        schema_verif_result: dict,
        output_dir: str,
        file_name: str,
        logger: logging.Logger,
    ) -> None:
    """
    Store the results schema verification
    """
    logger.info(f"Storing schema verification results to {output_dir}/{file_name}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    dataframe = pd.DataFrame(schema_verif_result)
    dataframe.to_csv(Path(f"{output_dir}/{file_name}.csv"), index=False)

    return None