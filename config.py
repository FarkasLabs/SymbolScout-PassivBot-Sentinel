import yaml
import logging
from schema import Schema, And, Use, Optional, Or

def load_and_validate_config(config_file='config.yml'):
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        schema = Schema({
            'symbolscout_endpoint': str,
            'check_interval': And(int, lambda n: n > 0),
            'news_monitoring': {
                'categories': [str],
                'sources': [str],
                'title_keywords': [str],
                'quote_currencies': [str],
                Optional('custom_filter'): Or(str, None)
            },
            'symbol_exclusion_strategy': {
                'remove_from_approved_coins': bool,
                'add_to_ignored_coins': bool
            },
            'passivbot': {
                'passivbot_folder': str,
                'mode': str,
                'tmuxp': {
                    'tmux_config_file': str,
                    'tmux_session_name': str,
                    'stop_command': str,
                    'start_command': str
                },
                'passivbot_config_files': [{
                    'config_file': str
                }]
            }
        })
        
        validated_config = schema.validate(config)
        logging.info("Configuration loaded and validated successfully")
        return validated_config
    except Exception as e:
        logging.error(f"Error in loading or validating configuration: {str(e)}")
        return None