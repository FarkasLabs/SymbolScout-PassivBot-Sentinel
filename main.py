import time
import schedule
from config import load_and_validate_config
from news_fetcher import fetch_news
from news_processor import extract_symbols, filter_news
from passivbot_config_updater import update_passivbot_configs
from state_manager import (
    load_last_processed_timestamp,
    get_new_articles,
    update_last_processed_timestamp,
)
from logger import logger


def process_news(config):
    try:
        last_processed_timestamp = load_last_processed_timestamp()
        logger.info(f"Last processed timestamp: {last_processed_timestamp}")

        news = fetch_news(config["symbolscout_endpoint"])

        if not news:
            logger.error("Failed to fetch news.")
            return

        new_articles = get_new_articles(news, last_processed_timestamp)

        if not new_articles:
            logger.info("No articles to process.")
            return

        filtered_news = filter_news({"news": new_articles}, config)

        quote_currencies = config["news_monitoring"]["quote_currencies"]

        symbols_to_exclude = set()
        for article in filtered_news:
            symbols = extract_symbols(article, quote_currencies)
            symbols_to_exclude.update(symbols)
            logger.info(
                f"New Article: {article['title']}\n  Category: {article['category']}\n  Symbols: {', '.join(symbols)}\n  Trading Pairs: {', '.join(article.get('trading_pairs', []))}"
            )

        if symbols_to_exclude:
            logger.info(f"Total symbols to exclude: {', '.join(symbols_to_exclude)}")
            update_passivbot_configs(filtered_news, config, symbols_to_exclude)
            logger.info("PassivBot configuration update completed")
        else:
            logger.info(
                "No symbols to exclude. Skipping PassivBot configuration update."
            )

        update_last_processed_timestamp(news)
        logger.info(
            f"Updated last processed timestamp to: {load_last_processed_timestamp()}"
        )
    except Exception as e:
        logger.error(f"Error in process_news: {str(e)}")


def main():
    logger.info("Started SymbolScout integration for PassivBot")

    config = load_and_validate_config()
    if not config:
        logger.error("Configuration loading or validation failed. Exiting.")
        return

    # Run process_news once immediately
    process_news(config)

    # Schedule future runs
    schedule.every(config["check_interval"]).seconds.do(process_news, config)

    logger.info(f"Scheduled to run every {config['check_interval']} seconds")

    last_log_time = time.time()
    log_interval = 60  # Log remaining time every 60 seconds

    while True:
        # Get the number of seconds until the next job
        idle_seconds = schedule.idle_seconds()

        if idle_seconds is None:
            logger.info("No more jobs scheduled. Exiting.")
            break

        current_time = time.time()
        if current_time - last_log_time >= log_interval:
            logger.info(f"Next update in {int(idle_seconds)} seconds")
            last_log_time = current_time

        # Sleep until the next job or for 1 second, whichever is shorter
        time.sleep(min(idle_seconds, 1))

        schedule.run_pending()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if (logger):
            logger.error(f"An error occurred: {str(e)}")
        else:
            print(f"An error occurred: {str(e)}")