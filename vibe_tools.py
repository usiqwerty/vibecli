import os
import subprocess

from fastmcp import FastMCP

mcp_server = FastMCP(
    name="Vibe Server",
    instructions="""Call write_file(filename: str, content: str) and read_file(filename: str) to operate with files.
Run list_dir(dir_name: str | None = None) to get directory contents.
Run run_tests() to run pytest""",
    on_duplicate_tools="error",
    on_duplicate_resources="error",
    on_duplicate_prompts="error"
)


@mcp_server.tool()
def run_tests() -> str:
    """run `pytest` command"""
    # Either use some API that provides comprehensive info about tests results
    # or just run os.system
    proc = subprocess.Popen("pytest", stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode()


@mcp_server.tool()
def write_file(filename: str, content: str) -> int:
    """Write text to file"""
    print(f"Writing file {filename}...")
    consent = input('"y" to approve: ')
    if consent != "y":
        return 0
    with open(filename, 'w', encoding='utf-8') as f:
        return f.write(content)

@mcp_server.tool()
def read_file(filename: str) -> str:
    """Read text from file"""
    print(f"Reading file {filename}...")
    with open(filename, encoding='utf-8') as f:
        return f.read() or ""

@mcp_server.tool()
def list_dir(dir_name: str | None = None) -> list[str]:
    """List files and subdirectories"""
    print(f"Reading directory {dir_name}...")
    entries = os.listdir(dir_name)
    for i, ent in enumerate(entries):
        if os.path.isdir(ent):
            entries[i] = ent + '/'
    return entries
