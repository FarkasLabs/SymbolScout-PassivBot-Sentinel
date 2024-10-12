import unittest
import json
import tempfile
import os
from passivbot_config_updater import update_passivbot_configs


class TestPassivbotConfigUpdater(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        self.sample_config = {
            "live": {
                "approved_coins": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "ADAUSDT"],
                "ignored_coins": [],
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

    def tearDown(self):
        os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_remove_from_approved_coins(self):
        news_articles = [{"symbols": "XRP,ADA", "category": "DELISTING"}]
        config = {
            "passivbot": {
                "passivbot_config_files": [{"config_file": self.config_path}],
                "trading_quote_currency": "USDT",
                "symbol_exclusion_strategy": {
                    "remove_from_approved_coins": True,
                    "add_to_ignored_coins": False,
                },
                "mode": "tmuxp",
                "tmuxp": {
                    "tmux_config_file": "dummy_path",
                    "tmux_session_name": "dummy_session",
                    "stop_command": "dummy_stop",
                    "start_command": "dummy_start",
                },
            }
        }
        symbols_to_exclude = {"XRP", "ADA"}

        update_passivbot_configs(news_articles, config, symbols_to_exclude)

        with open(self.config_path, "r") as f:
            updated_config = json.load(f)

        self.assertNotIn("XRPUSDT", updated_config["live"]["approved_coins"])
        self.assertNotIn("ADAUSDT", updated_config["live"]["approved_coins"])
        self.assertIn("BTCUSDT", updated_config["live"]["approved_coins"])
        self.assertIn("ETHUSDT", updated_config["live"]["approved_coins"])

    def test_add_to_ignored_coins(self):
        news_articles = [{"symbols": "XRP,ADA", "category": "DELISTING"}]
        config = {
            "passivbot": {
                "passivbot_config_files": [{"config_file": self.config_path}],
                "trading_quote_currency": "USDT",
                "symbol_exclusion_strategy": {
                    "remove_from_approved_coins": False,
                    "add_to_ignored_coins": True,
                },
                "mode": "tmuxp",
                "tmuxp": {
                    "tmux_config_file": "dummy_path",
                    "tmux_session_name": "dummy_session",
                    "stop_command": "dummy_stop",
                    "start_command": "dummy_start",
                },
            },
        }
        symbols_to_exclude = {"XRP", "ADA"}

        update_passivbot_configs(news_articles, config, symbols_to_exclude)

        with open(self.config_path, "r") as f:
            updated_config = json.load(f)

        self.assertIn("XRPUSDT", updated_config["live"]["ignored_coins"])
        self.assertIn("ADAUSDT", updated_config["live"]["ignored_coins"])
        self.assertEqual(
            len(updated_config["live"]["approved_coins"]), 4
        )  # No change in approved coins


if __name__ == "__main__":
    unittest.main()
