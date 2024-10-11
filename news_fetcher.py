import requests
import logging

def fetch_news(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        news = response.json()
        logging.info(f"Successfully fetched {len(news['news'])} news articles")
        return news
    except requests.RequestException as e:
        logging.error(f"Error fetching news: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching news: {str(e)}")
        return None