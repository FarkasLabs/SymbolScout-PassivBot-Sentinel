import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from logger import logger

def fetch_news(endpoint, max_retries=3, backoff_factor=0.3):
    # Create a retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    # Create an HTTP adapter with the retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Create a session and mount the adapter
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(endpoint, timeout=10)
        response.raise_for_status()
        news = response.json()
        logger.info(f"Successfully fetched {len(news['news'])} news articles")
        return news
    except requests.RequestException as e:
        logger.error(f"Error fetching news after {max_retries} retries: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching news: {str(e)}")
        return None
