from datetime import datetime, timezone
import unittest
from unittest.mock import patch, MagicMock
import main
import json
import tempfile
import os
import schedule

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

    @patch('main.fetch_news')
    @patch('main.filter_news')
    @patch('main.update_passivbot_configs')
    @patch('main.load_last_processed_timestamp')
    @patch('main.update_last_processed_timestamp')
    @patch('main.get_new_articles')
    @patch('main.extract_symbols')
    def test_process_news(self, mock_extract_symbols, mock_get_new_articles, mock_update_timestamp, mock_load_timestamp, mock_update_configs, mock_filter_news, mock_fetch_news):
        # Mock configuration
        mock_config = {
            'symbolscout_endpoint': 'https://test.com/api',
            'check_interval': 600,
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

        # Mock news fetch
        mock_news = {
            'news': [
                {
                    'title': 'XRP Delisting',
                    'category': 'DELISTING',
                    'symbols': 'XRP',
                    'trading_pairs': ['XRPUSDT'],
                    'created': '2024-10-08 04:10:23.613Z'
                }
            ]
        }
        mock_fetch_news.return_value = mock_news

        # Mock load_last_processed_timestamp
        mock_load_timestamp.return_value = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Mock get_new_articles
        mock_get_new_articles.return_value = mock_news['news']

        # Mock filter_news to return the same news
        mock_filter_news.return_value = mock_news['news']

        # Mock extract_symbols to return a non-empty set
        mock_extract_symbols.return_value = {'XRP'}

        # Run the process_news function
        main.process_news(mock_config)

        # Assertions
        mock_fetch_news.assert_called_once_with('https://test.com/api')
        mock_get_new_articles.assert_called_once()
        mock_filter_news.assert_called_once()
        mock_extract_symbols.assert_called()
        mock_update_configs.assert_called_once()
        mock_update_timestamp.assert_called_once()

    @patch('main.load_and_validate_config')
    @patch('schedule.every')
    @patch('time.sleep', side_effect=InterruptedError)  # To break the infinite loop
    def test_main_scheduling(self, mock_sleep, mock_schedule_every, mock_load_config):
        mock_config = {'check_interval': 600}
        mock_load_config.return_value = mock_config

        mock_job = MagicMock()
        mock_schedule_every.return_value.seconds.do.return_value = mock_job

        with self.assertRaises(InterruptedError):
            main.main()

        mock_load_config.assert_called_once()
        mock_schedule_every.assert_called_once_with(600)
        mock_schedule_every.return_value.seconds.do.assert_called_once_with(main.process_news, mock_config)

if __name__ == '__main__':
    unittest.main()