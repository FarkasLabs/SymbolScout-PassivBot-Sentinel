import unittest
import os
import json
from datetime import datetime, timezone, timedelta
from state_manager import (
    load_last_processed_timestamp,
    save_last_processed_timestamp,
    parse_datetime,
    get_new_articles,
    update_last_processed_timestamp
)

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_last_processed_state.json'
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_last_processed_timestamp_no_file(self):
        timestamp = load_last_processed_timestamp(self.test_file)
        expected_timestamp = datetime.min.replace(tzinfo=timezone.utc)
        
        self.assertEqual(timestamp, expected_timestamp)

    def test_timestamp_persistence(self):
        # Save a timestamp
        initial_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
        save_last_processed_timestamp(initial_timestamp, self.test_file)
        
        # Load the timestamp
        loaded_timestamp = load_last_processed_timestamp(self.test_file)
        
        self.assertEqual(initial_timestamp, loaded_timestamp)
        
        # Now remove the file and check if we get the minimum datetime
        os.remove(self.test_file)
        
        min_timestamp = load_last_processed_timestamp(self.test_file)
        expected_min_timestamp = datetime.min.replace(tzinfo=timezone.utc)
        
        self.assertEqual(min_timestamp, expected_min_timestamp)

    def test_save_and_load_last_processed_timestamp(self):
        test_timestamp = datetime.now(timezone.utc)
        save_last_processed_timestamp(test_timestamp)
        loaded_timestamp = load_last_processed_timestamp()
        self.assertEqual(test_timestamp, loaded_timestamp)

    def test_parse_datetime(self):
        test_string = "2024-10-08 04:10:23.613Z"
        parsed_datetime = parse_datetime(test_string)
        self.assertEqual(parsed_datetime.year, 2024)
        self.assertEqual(parsed_datetime.month, 10)
        self.assertEqual(parsed_datetime.day, 8)
        self.assertEqual(parsed_datetime.hour, 4)
        self.assertEqual(parsed_datetime.minute, 10)
        self.assertEqual(parsed_datetime.second, 23)
        self.assertEqual(parsed_datetime.microsecond, 613000)
        self.assertEqual(parsed_datetime.tzinfo, timezone.utc)

    def test_get_new_articles(self):
        last_processed = parse_datetime("2024-10-08 04:00:00.000Z")
        news = {
            'news': [
                {'created': "2024-10-08 03:59:59.999Z"},
                {'created': "2024-10-08 04:00:00.000Z"},
                {'created': "2024-10-08 04:00:00.001Z"},
                {'created': "2024-10-08 04:10:23.613Z"}
            ]
        }
        new_articles = get_new_articles(news, last_processed)
        self.assertEqual(len(new_articles), 2)
        self.assertEqual(new_articles[0]['created'], "2024-10-08 04:00:00.001Z")
        self.assertEqual(new_articles[1]['created'], "2024-10-08 04:10:23.613Z")

    def test_update_last_processed_timestamp(self):
        news = {
            'news': [
                {'created': "2024-10-08 03:59:59.999Z"},
                {'created': "2024-10-08 04:00:00.000Z"},
                {'created': "2024-10-08 04:10:23.613Z"}
            ]
        }
        update_last_processed_timestamp(news)
        loaded_timestamp = load_last_processed_timestamp()
        expected_timestamp = parse_datetime("2024-10-08 04:10:23.613Z")
        self.assertEqual(loaded_timestamp, expected_timestamp)

    def test_update_last_processed_timestamp_empty_news(self):
        initial_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
        save_last_processed_timestamp(initial_timestamp)
        
        news = {'news': []}
        update_last_processed_timestamp(news)
        loaded_timestamp = load_last_processed_timestamp()
        self.assertEqual(loaded_timestamp, initial_timestamp)

if __name__ == '__main__':
    unittest.main()