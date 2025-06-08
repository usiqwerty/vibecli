import asyncio
import json
import os
import pathlib
import signal
import traceback
from asyncio import CancelledError

from agents import Agent, ModelSettings, RunConfig, Runner, RunResult
from agents.mcp import MCPServerSse
from fastmcp import FastMCP
from openai import AsyncOpenAI, RateLimitError
from vibe.config import MODEL_NAME, history_file_path
from vibe.model_providers import TunedModelProvider


class VibecodeApp:
    openai_client: AsyncOpenAI
    filename: str
    fast_mcp_server: FastMCP
    run_config: RunConfig
    history: list[dict]
    log_level = 'warning'

    def __init__(self, fast_mcp_server: FastMCP, openai_client: AsyncOpenAI):
        self.fast_mcp_server = fast_mcp_server
        self.server = MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://localhost:8000/sse",
            },
        )
        self.openai_client = openai_client
        self.run_config = RunConfig(model=MODEL_NAME,
                                    model_provider=TunedModelProvider(openai_client=self.openai_client))
        self.history = []

    @property
    def agent_instructions(self):
        file_line = f"Current working file is {self.filename}. " if self.filename else ""

        return (f"Use provided the tools to complete given task. "
                "When you wrtie code you are expected to write it to file. "
                f"You are free to examine whole directory and do everything you consider related to solution. "
                + file_line)
    @property
    def __user_prompt(self):
        if self.filename:
            return f"{self.run_config.model}@{self.filename}> "
        else:
            return f"{self.run_config.model}> "

    def load_history(self, directory: str):
        """Load history for specifed directory"""
        with open(history_file_path, encoding='utf-8') as f:
            all_hists = json.load(f)
        # print(all_hists)
        current_dir_history = all_hists.get(directory, [])
        self.history = current_dir_history
        if self.history:
            print(f"History restored: {len(self.history)} messages")

    def set_history(self, new_history: list[dict]):
        self.history = new_history

        with open(history_file_path, 'r', encoding='utf-8') as f:
            all_hists = json.load(f)
        all_hists[os.getcwd()] = self.history
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump(all_hists, f)

    async def run_agent(self):
        async with self.server:
            agent = Agent(
                name="Assistant",
                instructions=self.agent_instructions,
                mcp_servers=[self.server],  # server should be set up by this moment
                model_settings=ModelSettings(tool_choice="auto"),
            )

            while True:
                message = input(self.__user_prompt).strip()

                if message in ['q', 'quit', 'exit']:
                    break
                if message.startswith('/'):
                    await self.process_command(message[1:], agent)
                    continue
                elif message.startswith('@'):
                    self.filename = message[1:] or None
                    continue

                print(f"Running: {message}")
                self.set_history(self.history + [{'type': 'message', 'role': 'user', 'content': message}])
                await self.make_llm_request(agent)

    def show_history(self):
        for entry in self.history:
            if entry['type'] == 'message':
                if isinstance(entry['content'], str):
                    print(f"== {entry['role']} ==")
                    print(' ' + entry['content'].replace('\n', '\n '))
                else:
                    for content_item in entry['content']:
                        if content_item['type'] == 'output_text':
                            print(f"== {entry['role']} ==")
                            print(' '+ content_item['text'].replace('\n', '\n '))
            elif entry['type'] == 'function_call':
                print(f"===> {entry['name']}({entry['arguments']})")
            elif entry['type'] == 'function_call_output':
                print(f"===>  Function call output: {len(entry['output'])} chars")
            else:
                print(entry)
    async def process_command(self, command: str, agent):
        if command == 'model':
            print(self.run_config.model)
            new_model_name = input('> ')
            if not new_model_name:
                return
            self.run_config.model = new_model_name
        elif command == 'hist':
            self.show_history()
        elif command == 'histpop':
            if self.history:
                self.history.pop()
            print(f"{len(self.history)} messages")
        elif command=='redo':
            await self.make_llm_request(agent)

    async def make_llm_request(self, agent):
        self.run_config.model_settings = ModelSettings(max_tokens=1000)
        try:
            result: RunResult = await Runner.run(starting_agent=agent,
                                                 input=self.history,
                                                 run_config=self.run_config)

            self.set_history(result.to_input_list())
            for r in result.raw_responses:
                in_t = r.usage.input_tokens
                out_t = r.usage.output_tokens
                print(f"Token usage: {in_t} in, {out_t} out")
            print('LLM:', result.final_output)
        except RateLimitError as e:
            print(e)
        except Exception as e:
            traceback.print_exception(e)
            self.show_history()
            print("There was a problem with request. Type /redo to repeat")

    async def main(self):
        server_task = asyncio.create_task(self.fast_mcp_server.run_http_async(transport='sse', log_level=self.log_level))
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
