import json

with open("config.json", encoding='utf-8') as f:
    config = json.load(f)
API_KEY = config['openrouter-key']
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "mistralai/mistral-small-3.1-24b-instruct:free"
