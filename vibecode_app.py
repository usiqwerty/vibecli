import asyncio
import os
import signal
from asyncio import CancelledError

from agents import Agent, ModelSettings, RunConfig, OpenAIChatCompletionsModel, Runner, RunResult
from agents.mcp import MCPServerSse
from fastmcp import FastMCP
from openai import AsyncOpenAI

from config import MODEL_NAME


class VibecodeApp:
    openai_client: AsyncOpenAI
    filename: str
    model_name: str
    fast_mcp_server: FastMCP

    def __init__(self, fast_mcp_server: FastMCP, openai_client: AsyncOpenAI):
        self.fast_mcp_server = fast_mcp_server
        self.server = MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://localhost:8000/sse",
            },
        )
        self.openai_client = openai_client

    async def run_agent(self):
        async with self.server:
            agent = Agent(
                name="Assistant",
                instructions=f"Use the tools to answer the questions. Main working file is {self.filename}",
                mcp_servers=[self.server],  # server should be set up by this moment
                model_settings=ModelSettings(tool_choice="auto"),
            )

            history = []
            while True:
                message = input(f"{self.model_name}@{self.filename}> ")

                if message in ['q', 'quit', 'exit']:
                    break
                print(f"Running: {message}")
                history.append({'type': 'message', 'role': 'user', 'content': message})
                run_config = RunConfig(model=OpenAIChatCompletionsModel(
                    model=MODEL_NAME,
                    openai_client=self.openai_client
                ))

                run_config.model_settings = ModelSettings(max_tokens=1000)
                result = await Runner.run(starting_agent=agent,
                                          input=history,
                                          run_config=run_config)
                result: RunResult

                history = result.to_input_list()
                print('LLM:', result.final_output)

    async def main(self):
        server_task = asyncio.create_task(self.fast_mcp_server.run_http_async(transport='sse', log_level='warning'))
        agent_task = asyncio.create_task(self.run_agent())
        try:
            await agent_task
        finally:
            server_task.cancel()
            try:
                await server_task
            except CancelledError:
                print("Server task cancelled")

        # Dirty trick, to deal with uvicorn's event loop
        os.kill(os.getpid(), signal.SIGTERM)
        print("Process was running after SIGTERM")
