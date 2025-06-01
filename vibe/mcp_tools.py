import os
from pathlib import Path
import subprocess

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

WORKING_DIRECTORY = Path(os.path.curdir).resolve()
mcp_server = FastMCP(
    name="Vibe Server",
    instructions="""This server provides folowwing tools for programming:
| function | description |
|-|-|
| write_file(filename: str, content: str) -> int | write text to file |
| read_file(filename: str) -> str | read text from file |
| list_dir(dir_name: str | None)-> list[str] | get directory contents |
| run_tests() | run pytest in subprocess | """,
    on_duplicate_tools="error",
    on_duplicate_resources="error",
    on_duplicate_prompts="error"
)


def check_path_under_cur_dir(path_string: str | None):
    if path_string is None:
        return

    path = Path(path_string).resolve()
    if WORKING_DIRECTORY not in path.parents:
        raise ToolError("You are not allowed to work outside working directory")


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
    check_path_under_cur_dir(filename)
    print(f"Writing file {filename}...")
    consent = input('"y" to approve: ')
    if consent != "y":
        return 0
    with open(filename, 'w', encoding='utf-8') as f:
        return f.write(content)


@mcp_server.tool()
def read_file(filename: str) -> str:
    """Read text from file"""
    check_path_under_cur_dir(filename)
    print(f"Reading file {filename}...")
    with open(filename, encoding='utf-8') as f:
        return f.read() or ""


@mcp_server.tool()
def list_dir(dir_name: str | None = None) -> list[str]:
    """List files and subdirectories"""
    check_path_under_cur_dir(dir_name)
    print(f"Reading directory {dir_name}...")
    entries = os.listdir(dir_name)
    for i, ent in enumerate(entries):
        if os.path.isdir(ent):
            entries[i] = ent + '/'
    return entries
