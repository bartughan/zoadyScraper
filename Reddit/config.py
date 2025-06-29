import os
import json

CONFIG_FILE = 'reddit_config.json'

def get_config_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)

def load_credentials():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return None

def save_credentials(client_id, client_secret, user_agent):
    config_path = get_config_path()
    creds = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }
    with open(config_path, 'w') as f:
        json.dump(creds, f)

def prompt_for_credentials():
    print('Reddit API credentials not found. Please enter them below:')
    client_id = input('Client ID: ').strip()
    client_secret = input('Client Secret: ').strip()
    user_agent = input('User Agent (any string identifying your app): ').strip()
    save_credentials(client_id, client_secret, user_agent)
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

def get_credentials():
    creds = load_credentials()
    if creds is None:
        creds = prompt_for_credentials()
    return creds 