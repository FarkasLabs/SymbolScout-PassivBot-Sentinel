import json
import os
from datetime import datetime, timezone
from logger import logger

STATE_FILE = 'last_processed_state.json'

def load_last_processed_timestamp(file_path=STATE_FILE):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
                return datetime.fromisoformat(state['last_processed_timestamp'])
        except (json.JSONDecodeError, KeyError):
            logger.info(f"Error reading {file_path}. Returning minimum datetime.")
    else:
        logger.info(f"No state file found at {file_path}. Returning minimum datetime.")
    
    return datetime.min.replace(tzinfo=timezone.utc)

def save_last_processed_timestamp(timestamp, file_path=STATE_FILE):
    with open(file_path, 'w') as f:
        json.dump({'last_processed_timestamp': timestamp.isoformat()}, f)

def parse_datetime(dt_string):
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

def get_new_articles(news, last_processed_timestamp):
    new_articles = [
        article for article in news['news']
        if parse_datetime(article['created']) > last_processed_timestamp
    ]
    return new_articles

def update_last_processed_timestamp(news):
    if news['news']:
        latest_timestamp = max(
            parse_datetime(article['created'])
            for article in news['news']
        )
        save_last_processed_timestamp(latest_timestamp)