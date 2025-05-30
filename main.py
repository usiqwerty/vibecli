import argparse
import asyncio
import logging

from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI

from config import API_KEY, BASE_URL, MODEL_NAME
from ui import logo
from vibe_tools import mcp_server
from vibecode_app import VibecodeApp

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    print(logo)
    print("An ultimate vibecoding CLI")
    print("Type q/quit/exit to exit")
    app = VibecodeApp(mcp_server, client)
    app.filename = args.input
    app.model_name = MODEL_NAME
    asyncio.run(app.main())
