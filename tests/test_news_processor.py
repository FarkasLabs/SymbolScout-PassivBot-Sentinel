import unittest
from news_processor import filter_news

class TestNewsProcessor(unittest.TestCase):
    def setUp(self):
        self.sample_news = {
            "last_updated": "2024-10-11T10:04:48.883Z",
            "news": [
                {
                    "symbols": "XEM,WAVES",
                    "trading_pairs": [],
                    "category": "TOKEN_SWAP",
                    "source": "Binance",
                    "title": "Notice on the Withdrawals of Delisted Tokens & Conversion of Selected Tokens to USDC (2024-10-08)"
                },
                {
                    "symbols": "XMR",
                    "trading_pairs": ["XMR/USD", "XMR/EUR", "XMR/BTC", "XMR/USDT"],
                    "category": "DELISTING",
                    "source": "Dailycoin.com",
                    "title": "Kraken Delists Monero in Privacy Coin Crackdown, XMR Dumps 15%"
                },
                {
                    "symbols": "BTC,USDT",
                    "trading_pairs": ["ORN/BTC", "ORN/USDT", "LUMIA/USDT"],
                    "category": "TOKEN_SWAP",
                    "source": "Crypto.News",
                    "title": "Binance will facilitate users swapping ORN to LUMIA this October"
                },
                {
                    "symbols": "BTC",
                    "trading_pairs": ["BTCUSD", "BTCUSDT"],
                    "category": "REGULATORY",
                    "source": "CoinDesk",
                    "title": "New Regulatory Framework for Cryptocurrencies"
                },
                {
                    "symbols": "LINK",
                    "trading_pairs": ["LINKUSDT", "LINKBTC"],
                    "category": "LISTING",
                    "source": "Binance",
                    "title": "Binance Lists Chainlink (LINK)"
                },
                {
                    "symbols": [],
                    "trading_pairs": ["ETH/USDT"],
                    "category": "DELISTING",
                    "source": "Kraken",
                    "title": "Kraken to Delist ETH/USDT pair"
                },
                {
                    "symbols": ["ADA", "DOT"],
                    "trading_pairs": ["ADA/USDT", "DOT/USDT"],
                    "category": "LISTING",
                    "source": "Coinbase",
                    "title": "Coinbase Adds Support for ADA and DOT"
                }
            ]
        }

    def test_filter_by_categories(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING', 'TOKEN_SWAP'],
                'sources': [],
                'quote_currencies': []
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 4)
        self.assertTrue(all(article['category'] in ['DELISTING', 'TOKEN_SWAP'] for article in filtered_news))

    def test_filter_by_sources(self):
        config = {
            'news_monitoring': {
                'categories': [],
                'sources': ['Binance'],
                'quote_currencies': []
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 2)
        self.assertTrue(all(article['source'] == 'Binance' for article in filtered_news))

    def test_filter_by_quote_currencies(self):
        config = {
            'news_monitoring': {
                'categories': [],
                'sources': [],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 6)
        for article in filtered_news:
            self.assertTrue(
                'USDT' in (article['symbols'] if isinstance(article['symbols'], str) else ' '.join(article['symbols'])) or 
                any('USDT' in pair for pair in article['trading_pairs'])
            )

    def test_filter_by_multiple_criteria(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING', 'TOKEN_SWAP'],
                'sources': ['Binance', 'Dailycoin.com'],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 1)
        self.assertEqual(filtered_news[0]['source'], 'Dailycoin.com')
        self.assertEqual(filtered_news[0]['category'], 'DELISTING')
        self.assertTrue('USDT' in filtered_news[0]['trading_pairs'][3])

    def test_filter_out_regulatory_category(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING', 'TOKEN_SWAP', 'LISTING'],
                'sources': [],
                'quote_currencies': []
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 6)
        self.assertTrue(all(article['category'] != 'REGULATORY' for article in filtered_news))

    def test_filter_trading_pairs_without_slash(self):
        config = {
            'news_monitoring': {
                'categories': [],
                'sources': [],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertTrue(any('LINKUSDT' in article['trading_pairs'] for article in filtered_news))

    def test_empty_symbols_list(self):
        config = {
            'news_monitoring': {
                'categories': ['DELISTING'],
                'sources': ['Kraken'],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 1)
        self.assertEqual(filtered_news[0]['symbols'], [])
        self.assertEqual(filtered_news[0]['trading_pairs'], ['ETH/USDT'])

    def test_symbols_as_array(self):
        config = {
            'news_monitoring': {
                'categories': ['LISTING'],
                'sources': ['Coinbase'],
                'quote_currencies': ['USDT']
            }
        }
        filtered_news = filter_news(self.sample_news, config)
        self.assertEqual(len(filtered_news), 1)
        self.assertIsInstance(filtered_news[0]['symbols'], list)
        self.assertEqual(set(filtered_news[0]['symbols']), {'ADA', 'DOT'})

if __name__ == '__main__':
    unittest.main()