def filter_news(news, config):
    filtered_news = news['news']
    
    categories = config['news_monitoring']['categories']
    sources = config['news_monitoring']['sources']
    quote_currencies = config['news_monitoring']['quote_currencies']

    if categories:
        filtered_news = [article for article in filtered_news if article['category'] in categories]

    if sources:
        filtered_news = [article for article in filtered_news if article['source'] in sources]

    if quote_currencies:
        filtered_news = [
            article for article in filtered_news 
            if any(currency in (article['symbols'] if isinstance(article['symbols'], str) else ' '.join(article['symbols']))
                   for currency in quote_currencies) or
            any(currency in pair.split('/')[-1] if '/' in pair else pair 
                for pair in article['trading_pairs'] 
                for currency in quote_currencies)
        ]

    return filtered_news