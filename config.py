import json

with open("config.json", encoding='utf-8') as f:
    config = json.load(f)
API_KEY = config['openrouter-key']
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "qwen/qwen3-0.6b-04-28:free"
