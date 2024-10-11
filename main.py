import logging
from config import load_and_validate_config
from news_fetcher import fetch_news
from news_processor import extract_symbols, filter_news
from passivbot_config_updater import update_passivbot_configs
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Starting SymbolScout integration for PassivBot")
    
    config = load_and_validate_config()
    if not config:
        logging.error("Configuration loading or validation failed. Exiting.")
        return

    news = fetch_news(config['symbolscout_endpoint'])
    if not news:
        logging.error("Failed to fetch news. Exiting.")
        return

    logging.info(f"Fetched {len(news['news'])} news articles")

    filtered_news = filter_news(news, config)
    logging.info(f"Filtered {len(filtered_news)} relevant news articles out of {len(news['news'])} total articles")

    quote_currencies = config['news_monitoring']['quote_currencies']
    
    symbols_to_exclude = set()
    for article in filtered_news:
        symbols = extract_symbols(article, quote_currencies)
        symbols_to_exclude.update(symbols)
        logging.info(f"Article: {article['title']}")
        logging.info(f"  Category: {article['category']}")
        logging.info(f"  Symbols (excluding quote currencies): {', '.join(symbols)}")
        logging.info(f"  Trading Pairs: {', '.join(article.get('trading_pairs', []))}")

    logging.info(f"Total symbols to exclude: {', '.join(symbols_to_exclude)}")

    # Update PassivBot configs based on the filtered news
    update_passivbot_configs(filtered_news, config, symbols_to_exclude)

    logging.info("PassivBot configuration update completed")

if __name__ == "__main__":
    main()