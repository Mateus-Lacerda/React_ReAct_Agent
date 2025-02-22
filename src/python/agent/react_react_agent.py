"""Module responsible for the ReactReActAgent class."""
import json
import os
import re
import subprocess
from typing import List

from dotenv import load_dotenv
from groq import BadRequestError, Groq
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from python.agent.prompt import (
    CODE_GENERATION_PROMPT,
    REACT_REACT_AGENT_PROMPT,
    README_SUMMARIZATION_PROMPT,
)
from python.agent.tools import TOOLS
from python.models.code import CodeData, CodeStatus
from python.utils.printer import print_assistant_message, print_function_message
from python.utils.search_tool import search_github

load_dotenv('.env.local')

os.environ["PYDEVD_WARN_EVALUATION_TIMEOUT"] = "60"

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PROJECT_PATH = os.getenv('PROJECT_PATH')

class ReactReActAgent:
    """Agent responsible for building React projects with ReAct."""
    def __init__(self, verbose: bool = False) -> None:
        self.client = Groq(
            api_key=GROQ_API_KEY
        )
        self.verbose = verbose
        self.additional_infos = []
        self.code_data = CodeData(path=PROJECT_PATH)
        self.code_status = CodeStatus()
        self._messages = [
            self.get_system_prompt()
        ]
        self.tools = TOOLS

    @property
    def messages(self) -> List[dict]:
        """The messages list with a buffer of 10 messages."""
        messages_list = self._messages[-10:]
        if messages_list[0].get("role") != "system":
            messages_list.insert(0, self.get_system_prompt())
        return messages_list

    def pop_message(self) -> None:
        """Pops the last message from the messages list."""
        self._messages.pop()

    def get_system_prompt(self) -> dict:
        """Gets the system prompt."""
        system_prompt = REACT_REACT_AGENT_PROMPT
        if self.additional_infos:
            system_prompt += "\n" + f"{self.additional_infos}"
        return {
            "role": "system",
            "content": system_prompt
        }

    def chat(self, first_message: str) -> None:
        """Starts the chat with the Groq API."""
        while True:
            response = self.get_response(first_message)
            print_assistant_message(response)
            user_input = input("You: ")
            if user_input == "exit":
                break
            first_message = user_input

    def generate_bare_response(self, system: str, message: str) -> str:
        """Generates a bare response from the Groq API."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": system
            }, {
                "role": "user",
                "content": message
            }],
            model='llama-3.3-70b-versatile',
        )
        return response.choices[0].message.content

    def get_response(
            self,
            message: str,
            role: str = "user",
            tool_call_depth: int = 0,
            tool_choice: str = 'auto'
            ) -> str | None:
        """Gets the response from the Groq API."""
        self._messages.append({
            "role": role,
            "content": message
        })
        try:
            response = self.client.chat.completions.create(
                messages=self.messages,
                model='llama3-70b-8192',
                tools=self.tools,
                tool_choice=tool_choice
            )
        except BadRequestError as e:
            if self.verbose:
                print(e)
            print_assistant_message("A generation error occurred, please try again.")
            self.pop_message()
            message = input("You: ")
            return self.get_response(message, role=role, tool_call_depth=tool_call_depth)
        print(response.choices[0].message)

        if (
            tool_calls := response.choices[0].message.tool_calls
            ) or (
            tool_calls := self.check_for_implicit_tool_call(response.choices[0].message.content)
            ):
            return self.process_tool_call(tool_calls, depth=tool_call_depth)

        self._messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
            })
        content = response.choices[0].message.content
        return content or "No response from the Groq API."

    def check_for_implicit_tool_call(self, message: str) -> List[ChatCompletionMessageToolCall] | None:
        """Checks for an implicit tool call in the assistants message."""
        text_list = message.split('\n')
        function_calls: List[ChatCompletionMessageToolCall] = []
        noise_text = []
        for text in text_list:
            # Sometimes the agent generates a function call with a json argument
            pattern = r'<function\s*=\s*([a-zA-Z0-9_]+)\s*(\{.*\})\s*>'
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                noise_text.append(text)
                continue
            function_name = match.group(1)
            json_args = match.group(2)

            try:
                _args = json.loads(json_args)
            except json.JSONDecodeError:
                noise_text.append(text)
                continue
            function_call = ChatCompletionMessageToolCall(
                function=Function(
                    arguments=json_args,
                    name=function_name
                )
            )
            function_calls.append(function_call)
        if function_calls != []:
            print_assistant_message('\n'.join(noise_text))
        return function_calls

    def process_tool_call(
            self,
            tool_calls: List[ChatCompletionMessageToolCall],
            depth: int = 0,
            max_depth: int = 5
            ) -> str:
        """Processes the tool calls from the Groq API."""
        if depth > max_depth:
            return "Max recursion depth reached."

        print(tool_calls)
        for tool_call in tool_calls:
            print_function_message(f"Processing tool call: {tool_call.function.name}", verbose=self.verbose)
            tool_name = tool_call.function.name
            if hasattr(self, tool_name):
                tool_args = json.loads(tool_call.function.arguments)
                tool_response = getattr(self, tool_name)(**tool_args)
                print_function_message(f"Tool response: {tool_response}", verbose=self.verbose)
                tool_prompt = f"This was the result of the tool call: {tool_response}. Generate a follow up response for the user."
                return self.get_response(tool_prompt, role="assistant", tool_call_depth=depth + 1)
            else:
                continue
        return self.get_response("No available tools where passed.", role="assistant", tool_call_depth=depth + 1)

    def search_github_pages(self, username: str) -> str:
        """
        Searches the user's github pages.

        :param str username: The user's github username. Must be only a string value!
        """
        url = f"https://api.github.com/users/{username}/repos"

        response = search_github(url, verbose=self.verbose)
        summarizations = []
        if not response:
            return "Error: Could not find the user's github pages."
        for item in response:
            summarization = self.generate_bare_response(README_SUMMARIZATION_PROMPT, item)
            if summarization:
                summarizations.append(summarization)
        final_summarization_prompt = f"Please make a general summary from these README files: {summarizations}"
        final_summary = self.get_response(final_summarization_prompt, tool_choice='none')
        self.additional_infos.append(final_summary)

        return "Github pages searched successfully."

    def store_info(self, info: str) -> str:
        """
        Stores the user's information.

        :param str info: The information to store.
        """
        if info not in self.additional_infos:
            self.additional_infos.append(info)
        return "Info stored successfully."

    def make_code(self, project_summary: str, project_name: str) -> str:
        """
        Generates the code for the project.

        :param str project_summary: The summary of the project.
        :param str project_name: The name of the project.
        """
        coding_prompt = f"\nO projeto é: {project_summary}"
        coding_prompt += f"\nAs informações específicas do projeto são: {self.additional_infos}"
        response = self.generate_bare_response(
            system=CODE_GENERATION_PROMPT,
            message=coding_prompt
            )
        code = re.search(r'```(.*?)```', response, re.DOTALL).group(1)
        code = code.removeprefix('javascript\n')
        self.code_data.code = code
        self.code_data.name = '_'.join(project_name.lower().split(' '))
        return code

    def run_code(self) -> str:
        """
        Runs the generated code to start the project.
        """
        if not self.code_data.is_complete():
            return "Attention: The assistant must save the code before running it."

        code_path = self.code_data.path
        project_name = self.code_data.name
        code = self.code_data.code

        if not self.code_status.project_created:
            creation_result = subprocess.run(
                ["yarn", "create", "react-app", project_name],
                cwd=code_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120
            )
            self.code_status.project_created = True
        else:
            creation_result = subprocess.CompletedProcess(
                args=["yarn", "create", "react-app", project_name],
                returncode=0,
                stdout=b"Project already created.",
                stderr=b""
            )

        if not self.code_status.code_saved:
            project_path = os.path.join(code_path, project_name)
            with open(os.path.join(project_path, "src", "App.js"), 'w') as file:
                file.write(code)

            installation_result = subprocess.run(
                ["yarn", "install"],
                cwd=project_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120
            )
            self.code_status.code_saved = True
        else:
            installation_result = subprocess.CompletedProcess(
                args=["yarn", "install"],
                returncode=0,
                stdout=b"Dependencies already installed.",
                stderr=b""
            )

        starting_result = subprocess.run(
            ["yarn", "start"],
            cwd=project_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        result = f"""
Creation result: {creation_result.stdout.decode('utf-8')}
Creation error: {creation_result.stderr.decode('utf-8')}\n
Installation result: {installation_result.stdout.decode('utf-8')}
Installation error: {installation_result.stderr.decode('utf-8')}\n
Starting result: {starting_result.stdout.decode('utf-8')}
Starting error: {starting_result.stderr.decode('utf-8')}\n
"""
        return result
