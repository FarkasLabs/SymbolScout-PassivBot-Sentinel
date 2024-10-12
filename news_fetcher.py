import requests
from logger import logger

def fetch_news(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        news = response.json()
        logger.info(f"Successfully fetched {len(news['news'])} news articles")
        return news
    except requests.RequestException as e:
        logger.error(f"Error fetching news: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching news: {str(e)}")
        return None