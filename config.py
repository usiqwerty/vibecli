import json

with open("config.json", encoding='utf-8') as f:
    config = json.load(f)
API_KEY = config['api-key']
BASE_URL = config['base-url']
MODEL_NAME = config['model-name']

# BASE_URL = "https://openrouter.ai/api/v1"
# MODEL_NAME = "mistralai/mistral-small-3.1-24b-instruct:free"
