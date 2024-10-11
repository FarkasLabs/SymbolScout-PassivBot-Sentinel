import logging
import time
import schedule
from config import load_and_validate_config
from news_fetcher import fetch_news
from news_processor import extract_symbols, filter_news
from passivbot_config_updater import update_passivbot_configs
from state_manager import (
    load_last_processed_timestamp,
    get_new_articles,
    update_last_processed_timestamp
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_news(config):
    last_processed_timestamp = load_last_processed_timestamp()
    logging.info(f"Last processed timestamp: {last_processed_timestamp}")
    
    news = fetch_news(config['symbolscout_endpoint'])
    
    if not news:
        logging.error("Failed to fetch news.")
        return

    new_articles = get_new_articles(news, last_processed_timestamp)
    
    logging.info(f"Found {len(new_articles)} new articles out of {len(news['news'])} total articles")

    if not new_articles:
        logging.info("No new articles to process.")
        return

    logging.info(f"Processing {len(new_articles)} new articles")

    filtered_news = filter_news({'news': new_articles}, config)
    
    quote_currencies = config['news_monitoring']['quote_currencies']
    
    symbols_to_exclude = set()
    for article in filtered_news:
        symbols = extract_symbols(article, quote_currencies)
        symbols_to_exclude.update(symbols)
        logging.info(f"Article: {article['title']}")
        logging.info(f"  Category: {article['category']}")
        logging.info(f"  Symbols (excluding quote currencies): {', '.join(symbols)}")
        logging.info(f"  Trading Pairs: {', '.join(article.get('trading_pairs', []))}")

    if symbols_to_exclude:
        logging.info(f"Total symbols to exclude: {', '.join(symbols_to_exclude)}")
        update_passivbot_configs(filtered_news, config, symbols_to_exclude)
        logging.info("PassivBot configuration update completed")
    else:
        logging.info("No symbols to exclude. Skipping PassivBot configuration update.")

    update_last_processed_timestamp(news)
    logging.info(f"Updated last processed timestamp to: {load_last_processed_timestamp()}")

def main():
    logging.info("Starting SymbolScout integration for PassivBot")
    
    config = load_and_validate_config()
    if not config:
        logging.error("Configuration loading or validation failed. Exiting.")
        return

    # Run process_news once immediately
    process_news(config)

    # Schedule future runs
    schedule.every(config['check_interval']).seconds.do(process_news, config)

    logging.info(f"Scheduled to run every {config['check_interval']} seconds")

    last_log_time = time.time()
    log_interval = 60  # Log remaining time every 60 seconds

    while True:
        # Get the number of seconds until the next job
        idle_seconds = schedule.idle_seconds()
        
        if idle_seconds is None:
            logging.info("No more jobs scheduled. Exiting.")
            break
        
        current_time = time.time()
        if current_time - last_log_time >= log_interval:
            logging.info(f"Next update in {int(idle_seconds)} seconds")
            last_log_time = current_time

        # Sleep until the next job or for 1 second, whichever is shorter
        time.sleep(min(idle_seconds, 1))
        
        schedule.run_pending()

if __name__ == "__main__":
    main()