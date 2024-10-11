import unittest
from unittest.mock import patch
from news_fetcher import fetch_news
import requests

class TestNewsFetcher(unittest.TestCase):
    @patch('requests.get')
    def test_successful_fetch(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            'news': [
                {'title': 'Test News 1'},
                {'title': 'Test News 2'}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        news = fetch_news('https://test-endpoint.com')
        self.assertIsNotNone(news)
        self.assertEqual(len(news['news']), 2)

    @patch('requests.get')
    def test_failed_fetch(self, mock_get):
        mock_get.side_effect = requests.RequestException('Network error')

        news = fetch_news('https://test-endpoint.com')
        self.assertIsNone(news)

if __name__ == '__main__':
    unittest.main()