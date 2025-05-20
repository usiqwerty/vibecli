import asyncio

from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled, RunConfig
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI

from config import API_KEY, BASE_URL, MODEL_NAME
from vibe_mcp import mcp_server

# run fastmcp run vibe_mcp.py:mcp_server --transport sse
# before running this, run the mcp-server-openai.py file

model = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(model, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


async def run_agent():
    server = MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    )
    async with server:
        agent = Agent(
            name="Assistant",
            instructions="Use the tools to answer the questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="auto"),
        )
        print('\n'.join(map(str, await agent.get_all_tools())))

        messages = []
        prev = None
        for message in messages:
            print(f"Running: {message}")
            run_config = RunConfig()
            run_config.model_settings = ModelSettings(max_tokens=1000)
            result = await Runner.run(starting_agent=agent, input=message, run_config=run_config,
                                      previous_response_id=prev)
            prev = result.last_response_id
            print(result.final_output)


async def main():
    server_task = asyncio.create_task(mcp_server.run_sse_async())
    agent_task = asyncio.create_task(run_agent())
    await asyncio.gather(server_task, agent_task)


if __name__ == "__main__":
    asyncio.run(main())
