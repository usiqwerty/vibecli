import argparse
import asyncio
import os.path

from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled, RunConfig
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI

from config import API_KEY, BASE_URL, MODEL_NAME
from vibe_mcp import mcp_server

model = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(model, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


async def run_agent(filename: str):
    server = MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    )
    async with server:
        agent = Agent(
            name="Assistant",
            instructions=f"Use the tools to answer the questions. Main working file is {filename}",
            mcp_servers=[server], # server should be set up by this moment
            model_settings=ModelSettings(tool_choice="auto"),
        )


        prev = None
        while True:
            message = input("input> ")
            if message in ['q', 'quit', 'exit']:
                break

            print(f"Running: {message}")
            run_config = RunConfig()
            run_config.model_settings = ModelSettings(max_tokens=1000)
            result = await Runner.run(starting_agent=agent, input=message, run_config=run_config,
                                      previous_response_id=prev)
            prev = result.last_response_id
            print('LLM:', result.final_output)

async def main(filename: str):
    server_task = asyncio.create_task(mcp_server.run_sse_async())
    agent_task = asyncio.create_task(run_agent(filename))
    # await asyncio.gather(server_task, agent_task)

    await asyncio.wait_for(agent_task, None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    if not os.path.exists(args.input):
        with open(args.input, 'w') as f:
            pass

    asyncio.run(main(args.input))
