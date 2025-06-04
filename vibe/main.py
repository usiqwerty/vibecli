import argparse
import asyncio
import logging
import os

from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI

from vibe.config import API_KEY, BASE_URL, MODEL_NAME
from vibe.ui import logo
from vibe.mcp_tools import mcp_server
from vibe.vibecode_app import VibecodeApp

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = VibecodeApp(mcp_server, client)
    app.filename = args.input
    app.model_name = MODEL_NAME

    if args.debug:
        logging_level = logging.DEBUG
        app.log_level = 'debug'
    else:
        logging_level = logging.WARNING
    logging.getLogger().setLevel(logging_level)
    logging.getLogger('FastMCP').setLevel(logging_level)
    logging.getLogger('openai.agents').setLevel(logging_level)

    print(logo)
    print("An ultimate vibecoding CLI")
    print("Type q/quit/exit to exit")
    app.load_history(os.getcwd())
    asyncio.run(app.main())
