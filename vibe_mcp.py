import asyncio
import os
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
def run_tests() -> str:
    # Either use some API that provides comprehensive info about tests results
    # or just run os.system
    proc = subprocess.Popen("pytest", stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode()


@mcp_server.tool()
def write_file(filename: str, content: str) -> int:
    print(f"Writing file {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        return f.write(content)

@mcp_server.tool()
def read_file(filename: str) -> str:
    print(f"Reading file {filename}...")
    with open(filename, encoding='utf-8') as f:
        return f.read()

@mcp_server.tool()
def list_dir(dir_name: str | None = None) -> list[str]:
    print(f"Reading directory {dir_name}...")
    entries = os.listdir(dir_name)
    for i, ent in enumerate(entries):
        if os.path.isdir(ent):
            entries[i] = ent + '/'
    return entries

if __name__ == "__main__":
    client = Client(mcp_server)
    async def call_tool():
        async with client:
            result = await client.call_tool("list_dir")
            print(result[0].text)

    asyncio.run(call_tool())
