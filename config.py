import yaml
import logging
import os
import string
from schema import Schema, And, Use, Optional, Or

class NestedTemplate(string.Template):
    def safe_substitute(self, mapping):
        # First, substitute any variables that are already in the mapping
        result = super().safe_substitute(mapping)
        
        # Then, check if there are any remaining variables to substitute
        while '$' in result:
            new_result = string.Template(result).safe_substitute(mapping)
            if new_result == result:
                break  # No more substitutions possible
            result = new_result
        
        return result

def load_yaml_with_substitutions(yaml_content, context):
    def string_constructor(loader, node):
        t = NestedTemplate(node.value)
        return t.safe_substitute(context)

    loader = yaml.SafeLoader
    loader.add_constructor('tag:yaml.org,2002:str', string_constructor)

    token_re = NestedTemplate.pattern
    loader.add_implicit_resolver('tag:yaml.org,2002:str', token_re, None)

    return yaml.load(yaml_content, Loader=loader)

def load_and_validate_config(config_file='config.yml'):
    try:
        with open(config_file, 'r') as file:
            yaml_content = file.read()

        # Create a context dictionary with environment variables
        context = os.environ.copy()
        # Add any additional variables you want to be available for substitution
        context['HOME'] = os.path.expanduser('~')

        config = load_yaml_with_substitutions(yaml_content, context)

        # Add passivbot_folder to context for nested substitutions
        if 'passivbot' in config and 'passivbot_folder' in config['passivbot']:
            context['passivbot_folder'] = config['passivbot']['passivbot_folder']

        # Perform a second pass of substitution for nested variables
        yaml_content = yaml.dump(config)
        config = load_yaml_with_substitutions(yaml_content, context)

        schema = Schema({
            'symbolscout_endpoint': str,
            'check_interval': And(int, lambda n: n > 0),
            'news_monitoring': {
                'categories': [str],
                'quote_currencies': [str]
            },
            'symbol_exclusion_strategy': {
                'remove_from_approved_coins': bool,
                'add_to_ignored_coins': bool
            },
            'passivbot': {
                'passivbot_folder': str,
                Optional('trading_quote_currency'): str,
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