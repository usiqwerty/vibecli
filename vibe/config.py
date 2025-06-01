import json
import os
import pathlib

home_path = pathlib.Path.home()
config_dir_path = os.path.join(home_path, ".vibe")
main_config_path = os.path.join(config_dir_path, "config.json")

try:
    with open(main_config_path, encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    os.makedirs(config_dir_path, exist_ok=True)
    __base_url  = input("Base URL: ")
    __api_key = input('API key: ')
    __model_name = input('Model name: ')
    config = {
        'api-key': __api_key,
        'base-url': __base_url,
        'model-name': __model_name
    }
    with open(main_config_path,'w', encoding='utf-8') as f:
        json.dump(config, f)

API_KEY = config['api-key']
BASE_URL = config['base-url']
MODEL_NAME = config['model-name']
