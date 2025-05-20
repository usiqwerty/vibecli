import argparse
import asyncio

from asyncio.exceptions import CancelledError

from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled, RunConfig, \
    RunResult
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from fastmcp import FastMCP
from openai import AsyncOpenAI

from config import API_KEY, BASE_URL
from vibe_mcp import mcp_server

model = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(model, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


class VibeService:
    filename: str
    fast_mcp_server: FastMCP

    def __init__(self, fast_mcp_server: FastMCP):
        self.fast_mcp_server = fast_mcp_server
        self.server = MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://localhost:8000/sse",
            },
        )

    async def run_agent(self):
        async with self.server:
            agent = Agent(
                name="Assistant",
                instructions=f"Use the tools to answer the questions. Main working file is {self.filename}",
                mcp_servers=[self.server],  # server should be set up by this moment
                model_settings=ModelSettings(tool_choice="auto"),
            )

            prev = None
            history = []
            while True:
                message = input(f"{self.filename}> ")

                if message in ['q', 'quit', 'exit']:
                    break
                print(f"Running: {message}")
                history.append({'type': 'message', 'role': 'user', 'content': message})
                run_config = RunConfig()
                run_config.model_settings = ModelSettings(max_tokens=400)
                result = await Runner.run(starting_agent=agent,
                                          input=history,
                                          run_config=run_config,
                                          previous_response_id=prev)
                prev = result.last_response_id
                result: RunResult

                history = result.to_input_list()
                print('LLM:', result.final_output)

    async def main(self):
        self.server_task = asyncio.create_task(self.fast_mcp_server.run_sse_async())
        self.agent_task = asyncio.create_task(self.run_agent())
        try:
            await self.agent_task
        finally:
            self.server_task.cancel()
            try:
                await self.server_task
            except CancelledError:
                print("server cancelled")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()


    app = VibeService(mcp_server)
    app.filename = args.input
    asyncio.run(app.main())
