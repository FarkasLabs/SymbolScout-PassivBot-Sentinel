import logging
from config import load_and_validate_config
from news_fetcher import fetch_news
from news_processor import extract_symbols, filter_news
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
    for article in news['news']:
        symbols = extract_symbols(article, quote_currencies)
        category_match = not config['news_monitoring']['categories'] or article['category'] in config['news_monitoring']['categories']
        
        trading_pairs = article.get('trading_pairs', [])
        if not trading_pairs:
            currency_match = True  # Always True if no trading pairs
        else:
            currency_match = any(currency in pair for pair in trading_pairs for currency in quote_currencies)
        
        kept = category_match and currency_match
        
        logging.info(f"Article: {article['title']}")
        logging.info(f"  Category: {article['category']} (Match: {category_match})")
        logging.info(f"  Symbols (excluding quote currencies): {', '.join(symbols)}")
        logging.info(f"  Trading Pairs: {', '.join(trading_pairs) if trading_pairs else 'None'}")
        logging.info(f"  Currency Match: {currency_match}")
        logging.info(f"  Kept: {kept}")

if __name__ == "__main__":
    main()