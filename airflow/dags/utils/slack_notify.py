import logging
import os
import dotenv
from pathlib import Path

import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from utils import logger as app_logger
import config

dotenv.load_dotenv()

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.


def send_slack_notification(
    schema_verif_dir: str,
    minimum_global_confidence_threshold: float,
    slack_bot_token: str,
    channel_id: str,
    logger: logging.Logger
) -> None:

    data_files = list(Path(schema_verif_dir).iterdir())
    for i in data_files:
        df = pd.read_csv(i)
        df_below_threshold = df[df['global_confidence'] < minimum_global_confidence_threshold]

        if df_below_threshold.empty:
            logger.info(f"All records in {i.name} meet the minimum global confidence threshold of {minimum_global_confidence_threshold}.")
        else:
            logger.warning(f"Records in {i.name} are below the minimum global confidence threshold of {minimum_global_confidence_threshold}.")
            logger.info("Sending Slack notification to alert the team...")
            client = WebClient(token=slack_bot_token)
            try:
                result = client.chat_postMessage(
                    channel=channel_id,
                    text=f"There are records in {i.name} that do not meet the minimum global confidence threshold of {minimum_global_confidence_threshold}."
                )
                logger.info(f"Message sent: {result}")

            except SlackApiError as e:
                logger.error(f"Error: {e}")

    return None