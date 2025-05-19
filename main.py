import asyncio
from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI

from config import API_KEY, BASE_URL, MODEL_NAME

# run fastmcp run vibe_mcp.py:mcp_server --transport sse
# before running this, run the mcp-server-openai.py file
# mcp_server.run(transport='sse')
model = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
set_default_openai_client(model, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


async def main():
    server = MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    )
    await server.connect()  # Initialize the server connection

    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use the `add` tool to add two numbers
    message = "Add these numbers: 7 and 22."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    await server.cleanup()  # Clean up the server connection


if __name__ == "__main__":
    asyncio.run(main())
