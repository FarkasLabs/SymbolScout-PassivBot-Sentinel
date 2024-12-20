import json
import os
import subprocess
from logger import logger


def determine_quote_currency(config_file_path, config):
    # First, check if it's specified in the main config
    if "trading_quote_currency" in config["passivbot"]:
        return config["passivbot"]["trading_quote_currency"]

    # If not, try to derive it from the PassivBot config file
    try:
        with open(config_file_path, "r") as f:
            passivbot_config = json.load(f)

        # Assume the first approved coin's suffix is the quote currency
        if passivbot_config["live"]["approved_coins"]:
            first_coin = passivbot_config["live"]["approved_coins"][0]
            for common_quote in ["USDT", "BUSD", "USD", "USDC", "BTC", "ETH"]:
                if first_coin.endswith(common_quote):
                    return common_quote

        # If we couldn't determine it, log a warning and use a default
        logger.error(
            f"Couldn't determine quote currency for {config_file_path}. Using USDT as default."
        )
        return "USDT"
    except Exception as e:
        logger.error(
            f"Error determining quote currency from {config_file_path}: {str(e)}. Using USDT as default."
        )
        return "USDT"


def restart_passivbot_instances(config):
    tmuxp_config = config["passivbot"]["tmuxp"]

    # Stop existing PassivBot instances
    try:
        logger.info(f"Executing stop command: {tmuxp_config['stop_command']}")
        subprocess.run(tmuxp_config["stop_command"], shell=True, check=True)
        logger.info("Stopped existing PassivBot instances")
    except subprocess.CalledProcessError as e:
        if "session not found" in str(e).lower():
            logger.info("No existing PassivBot session found to stop")
        else:
            logger.error(f"Error stopping PassivBot instances: {str(e)}")
            return  # Exit the function if we can't stop existing instances

    # Start new PassivBot instances
    try:
        logger.info(
            f"Executing start command: {tmuxp_config['start_command']}"
        )
        subprocess.run(tmuxp_config["start_command"], shell=True, check=True)
        logger.info("Config Update: Successfully restarted PassivBot instances")
    except subprocess.CalledProcessError as e:
        error_message = f"Error restarting PassivBot instances: {str(e)}"
        logger.error(error_message)


def update_passivbot_configs(news_articles, config, symbols_to_exclude):
    changes_made = False
    for config_file in config["passivbot"]["passivbot_config_files"]:
        quote_currency = determine_quote_currency(config_file["config_file"], config)
        if update_single_config(
            config_file["config_file"],
            symbols_to_exclude,
            config["passivbot"]["symbol_exclusion_strategy"],
            quote_currency,
        ):
            changes_made = True

    if changes_made:
        logger.info(
            "Changes were made to PassivBot configurations. Restarting instances..."
        )
        restart_passivbot_instances(config)
    else:
        logger.info(
            "No changes were made to PassivBot configurations. Skipping restart."
        )


def update_single_config(
    config_file_path, symbols_to_exclude, exclusion_strategy, quote_currency
):
    try:
        config_file_path = os.path.expanduser(os.path.expandvars(config_file_path))

        logger.info(f"Attempting to update config file: {config_file_path}")

        if not os.path.exists(config_file_path):
            logger.error(f"Config file does not exist: {config_file_path}")
            return False

        with open(config_file_path, "r") as f:
            passivbot_config = json.load(f)

        original_config = json.dumps(passivbot_config)

        logger.info(f"Symbols to exclude: {', '.join(symbols_to_exclude)}")
        logger.info(
            f"Current approved_coins: {', '.join(passivbot_config['live']['approved_coins'])}"
        )
        logger.info(
            f"Current ignored_coins: {', '.join(passivbot_config['live'].get('ignored_coins', []))}"
        )

        removed_coins = set()
        added_to_ignored = set()

        logger.info(f"Using quote currency: {quote_currency}")

        if exclusion_strategy["remove_from_approved_coins"]:
            original_approved_coins = set(passivbot_config["live"]["approved_coins"])
            for coin in original_approved_coins:
                base_currency = coin.rstrip(quote_currency)
                if base_currency in symbols_to_exclude:
                    passivbot_config["live"]["approved_coins"].remove(coin)
                    removed_coins.add(coin)
                    logger.info(
                        f"Removing {coin} from approved_coins (matches {base_currency})"
                    )

        if exclusion_strategy["add_to_ignored_coins"]:
            if "ignored_coins" not in passivbot_config["live"]:
                passivbot_config["live"]["ignored_coins"] = []

            for symbol in symbols_to_exclude:
                coin = f"{symbol}{quote_currency}"
                if coin not in passivbot_config["live"]["ignored_coins"]:
                    passivbot_config["live"]["ignored_coins"].append(coin)
                    added_to_ignored.add(coin)
                    logger.info(f"Adding {coin} to ignored_coins (matches {symbol})")

        if removed_coins:
            logger.info(
                f"Config Update: Removed from approved_coins in {os.path.basename(config_file_path)}: {', '.join(removed_coins)}"
            )
        else:
            logger.info(
                f"No coins removed from approved_coins in {os.path.basename(config_file_path)}"
            )

        if added_to_ignored:
            logger.info(
                f"Config Update: Added to ignored_coins in {os.path.basename(config_file_path)}: {', '.join(added_to_ignored)}"
            )
        else:
            logger.info(
                f"No coins added to ignored_coins in {os.path.basename(config_file_path)}"
            )

        if json.dumps(passivbot_config) != original_config:
            with open(config_file_path, "w") as f:
                json.dump(passivbot_config, f, indent=4)
            logger.info(f"Updated PassivBot config file: {config_file_path}")
            logger.info(
                f"Final approved_coins: {', '.join(passivbot_config['live']['approved_coins'])}"
            )
            logger.info(
                f"Final ignored_coins: {', '.join(passivbot_config['live'].get('ignored_coins', []))}"
            )
            return True
        else:
            logger.info(f"No changes were necessary for {config_file_path}")
            return False

    except Exception as e:
        logger.error(
            f"Error updating PassivBot config file {config_file_path}: {str(e)}"
        )
        return False
