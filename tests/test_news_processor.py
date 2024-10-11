import unittest
from news_processor import filter_news, extract_symbols

class TestNewsProcessor(unittest.TestCase):
    def setUp(self):
        self.sample_news = {
            "last_updated": "2024-10-11T10:04:48.883Z",
            "news": [
                {
                    "symbols": "XEM,WAVES",
                    "trading_pairs": [],
                    "category": "TOKEN_SWAP",
                    "title": "Notice on the Withdrawals of Delisted Tokens & Conversion of Selected Tokens to USDC (2024-10-08)"
                },
                {
                    "symbols": "XMR",
                    "trading_pairs": ["XMR/USD", "XMR/EUR", "XMR/BTC", "XMR/USDT"],
                    "category": "DELISTING",
                    "title": "Kraken Delists Monero in Privacy Coin Crackdown, XMR Dumps 15%"
                },
                {
                    "symbols": "BTC,USDT",
                    "trading_pairs": ["ORN/BTC", "ORN/USDT", "LUMIA/USDT"],
                    "category": "TOKEN_SWAP",
                    "title": "Binance will facilitate users swapping ORN to LUMIA this October"
                },
                {
                    "symbols": "BTC",
                    "trading_pairs": ["BTCUSD", "BTCUSDT"],
                    "category": "REGULATORY",
                    "title": "New Regulatory Framework for Cryptocurrencies"
                }
            ]
        }

    def test_filter_by_categories(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING', 'TOKEN_SWAP'],
                'quote_currencies': []
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 3)
        self.assertTrue(all(article['category'] in ['DELISTING', 'TOKEN_SWAP'] for article in filtered_news))

    def test_filter_by_quote_currencies(self):
        config = {
            'news_monitoring': {
                'categories': [],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 4)
        for article in filtered_news:
            if article['trading_pairs']:
                self.assertTrue(any('USDT' in pair for pair in article['trading_pairs']))
            else:
                # For articles with empty trading pairs, we assume they pass the filter
                self.assertEqual(article['trading_pairs'], [])

    def test_filter_by_multiple_criteria(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING', 'TOKEN_SWAP'],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 3)
        for article in filtered_news:
            self.assertTrue(article['category'] in ['DELISTING', 'TOKEN_SWAP'])
            if article['trading_pairs']:
                self.assertTrue(any('USDT' in pair for pair in article['trading_pairs']))

    def test_empty_trading_pairs(self):
        config = {
            'news_monitoring': {
                'categories': ['TOKEN_SWAP'],
                'quote_currencies': ['XEM', 'WAVES']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 1)
        self.assertEqual(filtered_news[0]['category'], 'TOKEN_SWAP')
        self.assertEqual(filtered_news[0]['trading_pairs'], [])

    def test_extract_symbols(self):
        article = {
            "symbols": "BTC,USDT",
            "trading_pairs": ["ORN/BTC", "ORN/USDT", "LUMIA/USDT"],
        }
        quote_currencies = ['USDT', 'USD']
        symbols = extract_symbols(article, quote_currencies)
        self.assertEqual(symbols, {'BTC', 'ORN', 'LUMIA'})

if __name__ == '__main__':
    unittest.main()