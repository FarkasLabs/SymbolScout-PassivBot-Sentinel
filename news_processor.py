import logging
import re

def extract_symbols(article, quote_currencies):
    symbols = set()
    
    # Extract from 'symbols' field
    if isinstance(article['symbols'], str):
        symbols.update(article['symbols'].replace(' ', '').split(','))
    elif isinstance(article['symbols'], list):
        symbols.update(article['symbols'])
    
    # Extract from trading pairs
    for pair in article.get('trading_pairs', []):
        symbols.update(re.split(r'[/\-]', pair))
    
    # Remove quote currencies from the symbols
    symbols = symbols - set(quote_currencies)
    
    return symbols

def filter_news(news, config):
    all_news = news['news']
    
    categories = config['news_monitoring']['categories']
    quote_currencies = config['news_monitoring']['quote_currencies']

    logging.info(f"Filtering criteria - Categories: {categories}, Quote Currencies: {quote_currencies}")

    def matches_criteria(article):
        category_match = not categories or article['category'] in categories
        
        trading_pairs = article.get('trading_pairs', [])
        if not trading_pairs:
            return category_match  # If no trading pairs, only check category
        
        currency_match = not quote_currencies or any(currency in pair for pair in trading_pairs for currency in quote_currencies)
        
        return category_match and currency_match

    filtered_news = [article for article in all_news if matches_criteria(article)]

    for article in filtered_news:
        logging.info(f"Kept article: {article['title']} (Category: {article['category']})")

    return filtered_news