import unittest
import tempfile
import os
from config import load_and_validate_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yml")

    def tearDown(self):
        os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_valid_config(self):
        config_content = """
        symbolscout_endpoint: "https://symbolscout.farkaslabs.xyz/api/news/breaking"
        check_interval: 600
        news_monitoring:
            categories:
                - "DELISTING"
                - "TOKEN_SWAP"
            quote_currencies:
                - "USDT"
                - "USDC"
        passivbot:
            passivbot_folder: "~/passivbot"
            symbol_exclusion_strategy:
                remove_from_approved_coins: true
                add_to_ignored_coins: false
            mode: "tmuxp"
            tmuxp:
                tmux_config_file: "./passivbot-tmux-sessions-example.yml"
                tmux_session_name: "passivbot_instances"
                stop_command: "tmux has-session -t {tmux_session_name} && tmux kill-session -t {tmux_session_name} || true"
                start_command: "tmuxp load -d {tmux_config_file}"
            passivbot_config_files:
                - config_file: "{passivbot_folder}/configs/forager/bybit_01.json"
        """

        with open(self.config_path, "w") as f:
            f.write(config_content)

        config = load_and_validate_config(self.config_path)
        self.assertIsNotNone(config)
        self.assertEqual(config["check_interval"], 600)
        self.assertEqual(len(config["news_monitoring"]["categories"]), 2)

    def test_invalid_config(self):
        invalid_config_content = """
        symbolscout_endpoint: "https://symbolscout.farkaslabs.xyz/api/news/breaking"
        check_interval: "not an integer"  # This should cause a validation error
        news_monitoring:
            categories: []
            quote_currencies: []
        passivbot:
            passivbot_folder: "~/passivbot"
            symbol_exclusion_strategy:
                remove_from_approved_coins: true
                add_to_ignored_coins: false
            mode: "tmuxp"
            tmuxp:
                tmux_config_file: "./passivbot-tmux-sessions-example.yml"
                tmux_session_name: "passivbot_instances"
                stop_command: "tmux has-session -t {tmux_session_name} && tmux kill-session -t {tmux_session_name} || true"
                start_command: "tmuxp load -d {tmux_config_file}"
            passivbot_config_files:
                - config_file: "{passivbot_folder}/configs/forager/bybit_01.json"
        notifications:
            apprise_urls: []
            notify_on:
                errors: true
                config_updates: true
                new_news: true
            """

        with open(self.config_path, "w") as f:
            f.write(invalid_config_content)

        with self.assertRaises(ValueError):
            load_and_validate_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
