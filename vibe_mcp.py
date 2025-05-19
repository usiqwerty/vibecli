import asyncio
import pathlib
import subprocess

from fastmcp import FastMCP, Client

mcp_server = FastMCP(
    name="Vibe Server",
    instructions="This server provides tools for programming",
    on_duplicate_tools="error",
    on_duplicate_resources="error",
    on_duplicate_prompts="error"
)


@mcp_server.tool()
def run_tests():
    # Either use some API that provides comprehensive info about tests results
    # or just run os.system
    proc = subprocess.Popen("pytest", stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode()


@mcp_server.tool()
def write_file(filename: str, content: str):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


@mcp_server.resource("resource://{filename}")
def read_file(filename: str):
    with open(filename, encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    client = Client(mcp_server)


    async def call_tool():
        async with client:
            result = await client.call_tool("run_tests")
            print(result)

    asyncio.run(call_tool())
