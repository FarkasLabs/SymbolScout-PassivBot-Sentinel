import json
import logging
import os

def determine_quote_currency(config_file_path, config):
    # First, check if it's specified in the main config
    if 'trading_quote_currency' in config['passivbot']:
        return config['passivbot']['trading_quote_currency']
    
    # If not, try to derive it from the PassivBot config file
    try:
        with open(config_file_path, 'r') as f:
            passivbot_config = json.load(f)
        
        # Assume the first approved coin's suffix is the quote currency
        if passivbot_config['live']['approved_coins']:
            first_coin = passivbot_config['live']['approved_coins'][0]
            for common_quote in ['USDT', 'BUSD', 'USD', 'USDC', 'BTC', 'ETH']:
                if first_coin.endswith(common_quote):
                    return common_quote
        
        # If we couldn't determine it, log a warning and use a default
        logging.warning(f"Couldn't determine quote currency for {config_file_path}. Using USDT as default.")
        return 'USDT'
    except Exception as e:
        logging.error(f"Error determining quote currency from {config_file_path}: {str(e)}. Using USDT as default.")
        return 'USDT'

def update_passivbot_configs(news_articles, config, symbols_to_exclude):
    for config_file in config['passivbot']['passivbot_config_files']:
        quote_currency = determine_quote_currency(config_file['config_file'], config)
        update_single_config(config_file['config_file'], symbols_to_exclude, config['symbol_exclusion_strategy'], quote_currency)

def update_single_config(config_file_path, symbols_to_exclude, exclusion_strategy, quote_currency):
    try:
        config_file_path = os.path.expanduser(os.path.expandvars(config_file_path))
        
        logging.info(f"Attempting to update config file: {config_file_path}")

        if not os.path.exists(config_file_path):
            logging.error(f"Config file does not exist: {config_file_path}")
            return

        with open(config_file_path, 'r') as f:
            passivbot_config = json.load(f)

        logging.info(f"Symbols to exclude: {', '.join(symbols_to_exclude)}")
        logging.info(f"Current approved_coins: {', '.join(passivbot_config['live']['approved_coins'])}")
        logging.info(f"Current ignored_coins: {', '.join(passivbot_config['live'].get('ignored_coins', []))}")

        removed_coins = set()
        added_to_ignored = set()
        
        logging.info(f"Using quote currency: {quote_currency}")

        if exclusion_strategy['remove_from_approved_coins']:
            original_approved_coins = set(passivbot_config['live']['approved_coins'])
            for coin in original_approved_coins:
                base_currency = coin.rstrip(quote_currency)
                if base_currency in symbols_to_exclude:
                    passivbot_config['live']['approved_coins'].remove(coin)
                    removed_coins.add(coin)
                    logging.info(f"Removing {coin} from approved_coins (matches {base_currency})")

        if exclusion_strategy['add_to_ignored_coins']:
            if 'ignored_coins' not in passivbot_config['live']:
                passivbot_config['live']['ignored_coins'] = []
            
            for symbol in symbols_to_exclude:
                coin = f"{symbol}{quote_currency}"
                if coin not in passivbot_config['live']['ignored_coins']:
                    passivbot_config['live']['ignored_coins'].append(coin)
                    added_to_ignored.add(coin)
                    logging.info(f"Adding {coin} to ignored_coins (matches {symbol})")

        if removed_coins:
            logging.info(f"Removed from approved_coins in {os.path.basename(config_file_path)}: {', '.join(removed_coins)}")
        else:
            logging.info(f"No coins removed from approved_coins in {os.path.basename(config_file_path)}")

        if added_to_ignored:
            logging.info(f"Added to ignored_coins in {os.path.basename(config_file_path)}: {', '.join(added_to_ignored)}")
        else:
            logging.info(f"No coins added to ignored_coins in {os.path.basename(config_file_path)}")

        with open(config_file_path, 'w') as f:
            json.dump(passivbot_config, f, indent=4)

        logging.info(f"Updated PassivBot config file: {config_file_path}")
        logging.info(f"Final approved_coins: {', '.join(passivbot_config['live']['approved_coins'])}")
        logging.info(f"Final ignored_coins: {', '.join(passivbot_config['live'].get('ignored_coins', []))}")
    except Exception as e:
        logging.error(f"Error updating PassivBot config file {config_file_path}: {str(e)}")