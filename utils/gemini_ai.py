import json
from pathlib import Path

from utils import logger
import config

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

def call_gemini(sample_data: str, project_id: str, location: str) -> dict:

    vertexai.init(project=project_id, location=location)

    """Calls Gemini Flash with structured output schema enforcement."""
    model = GenerativeModel(
        str(config.GEMINI_MODEL),
        system_instruction=config.GEMINI_SYSTEM_PROMPT
    )
    response = model.generate_content(
        f"RAW_DATA_SAMPLE:\n{sample_data}",
        generation_config=config.GEMINI_GENERATION_CONFIG
    )
    return json.loads(response.text.replace('```','').replace('json','')) #type: ignore