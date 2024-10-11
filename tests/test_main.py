import unittest
from unittest.mock import patch, MagicMock
import main
import json
import tempfile
import os

class TestMain(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        self.sample_passivbot_config = {
            "live": {
                "approved_coins": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "ADAUSDT"],
                "ignored_coins": []
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.sample_passivbot_config, f)

    def tearDown(self):
        os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    @patch('main.load_and_validate_config')
    @patch('main.fetch_news')
    @patch('main.filter_news')
    def test_main_flow(self, mock_filter_news, mock_fetch_news, mock_load_config):
        # Mock configuration
        mock_config = {
            'symbolscout_endpoint': 'https://test.com/api',
            'news_monitoring': {
                'quote_currencies': ['USDT'],
                'categories': ['DELISTING']
            },
            'symbol_exclusion_strategy': {
                'remove_from_approved_coins': True,
                'add_to_ignored_coins': False
            },
            'passivbot': {
                'passivbot_config_files': [{'config_file': self.config_path}]
            }
        }
        mock_load_config.return_value = mock_config

        # Mock news fetch
        mock_news = {
            'news': [
                {
                    'title': 'XRP Delisting',
                    'category': 'DELISTING',
                    'symbols': 'XRP',
                    'trading_pairs': ['XRPUSDT']
                }
            ]
        }
        mock_fetch_news.return_value = mock_news

        # Mock news filtering (returning the same news as it matches our criteria)
        mock_filter_news.return_value = mock_news['news']

        # Run the main function
        main.main()

        # Assertions
        mock_load_config.assert_called_once()
        mock_fetch_news.assert_called_once_with('https://test.com/api')
        mock_filter_news.assert_called_once()

        # Check if the PassivBot config was updated correctly
        with open(self.config_path, 'r') as f:
            updated_config = json.load(f)
        self.assertNotIn('XRPUSDT', updated_config['live']['approved_coins'])
        self.assertIn('BTCUSDT', updated_config['live']['approved_coins'])
        self.assertIn('ETHUSDT', updated_config['live']['approved_coins'])
        self.assertIn('ADAUSDT', updated_config['live']['approved_coins'])

if __name__ == '__main__':
    unittest.main()