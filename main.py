import logging
from config import load_and_validate_config
from news_fetcher import fetch_news
from news_processor import filter_news

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting SymbolScout integration for PassivBot")
    
    # Load and validate configuration
    config = load_and_validate_config()
    if not config:
        logging.error("Configuration loading or validation failed. Exiting.")
        return

    # Fetch news
    news = fetch_news(config['symbolscout_endpoint'])
    if not news:
        logging.error("Failed to fetch news. Exiting.")
        return

    # Filter news based on configuration
    filtered_news = filter_news(news, config)
    logging.info(f"Filtered {len(filtered_news)} relevant news articles")

    # TODO: Update PassivBot configuration based on filtered news

if __name__ == "__main__":
    main()