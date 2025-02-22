"""Module responsible for the ReactReActAgent class."""
import json
import os
import re
import subprocess
from typing import List

from dotenv import load_dotenv
from groq import BadRequestError, Groq
from groq.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from python.agent.prompt import REACT_REACT_AGENT_PROMPT, README_SUMMARIZATION_PROMPT
from python.agent.tools import TOOLS
from python.models.code_data import CodeData
from python.utils.printer import print_assistant_message, print_function_message
from python.utils.search_tool import search_github

load_dotenv('.env.local')

GROQ_API_KEY = os.getenv('GROK_API_KEY')
PROJECT_PATH = os.getenv('PROJECT_PATH')

class ReactReActAgent:
    """Agent responsible for building React projects with ReAct."""
    def __init__(self, verbose: bool = False) -> None:
        self.client = Groq(
            api_key=GROQ_API_KEY
        )
        self.verbose = verbose
        self.additional_infos = []
        self.code_data = CodeData()
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
        """Starts the chat with the Grok API."""
        while True:
            response = self.get_response(first_message)
            print_assistant_message(response)
            user_input = input("You: ")
            if user_input == "exit":
                break
            first_message = user_input

    def generate_bare_response(self, system: str, message: str) -> str:
        """Generates a bare response from the Grok API."""
        response = self.client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": system
            }, {
                "role": "user",
                "content": message
            }],
            model='llama3-70b-8192',
        )
        return response.choices[0].message.content

    def get_response(
            self,
            message: str,
            role: str = "user",
            tool_call_depth: int = 0,
            tool_choice: str = 'auto'
            ) -> str | None:
        """Gets the response from the Grok API."""
        self._messages.append({
            "role": role,
            "content": message
        })
        try:
            response = self.client.chat.completions.create(
                messages=self.messages,
                model='llama-3.3-70b-versatile',
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
        return content or "No response from the Grok API."

    def check_for_implicit_tool_call(self, message: str) -> List[ChatCompletionMessageToolCall] | None:
        """Checks for an implicit tool call in the assistants message."""
        text_list = message.split('\n')
        function_calls: List[ChatCompletionMessageToolCall] = []
        for text in text_list:
            # TODO: Improve this logic to check for implicit tool calls.
            if "<function=" in text:
                function_name = text.split("<function=")[1].split(" ")[0]
                try:
                    function_arguments = eval(text.split("<function=")[1].split(" ")[1])
                except SyntaxError:
                    return None
                function_call = ChatCompletionMessageToolCall(
                    id="",
                    function={
                        "name": function_name,
                        "arguments": function_arguments
                    },
                    type="function"
                )
                function_calls.append(function_call)

        return function_calls

    def process_tool_call(
            self,
            tool_calls: List[ChatCompletionMessageToolCall],
            depth: int = 0,
            max_depth: int = 5
            ) -> str:
        """Processes the tool calls from the Grok API."""
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
                tool_prompt = f"This was the result of the tool call: {tool_response}. You can continue answering the user."
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

        response = search_github(url)
        if not response:
            return "Error: Could not find the user's github pages."
        for item in response:
            summarization = self.generate_bare_response(README_SUMMARIZATION_PROMPT, item)
            if summarization:
                self.additional_infos.append(summarization)
        return "Github pages searched successfully."

    def store_info(self, info: str) -> str:
        """
        Stores the user's information.

        :param str info: The information to store.
        """
        if info not in self.additional_infos:
            self.additional_infos.append(info)
        return "Info stored successfully."

    def make_code(self, idea: str) -> str:
        """
        Generates the code for the project.

        :param str idea: The idea for the project.
        """
        coding_prompt = """
You must now generate the code for the project.
Remember to write consistent and clean javascript code.
Return the code enclosed in triple sticks.
Remember: You need to generate a full single page React application.
Don't forget to include the necessary dependencies, styles and scripts.
Example:
```
function myFunction() {
    return "Hello World!";
}
```
"""
        coding_prompt += f"\nO projeto é: {idea}"
        response = self.get_response(coding_prompt, tool_choice='none')
        code = re.search(r'```(.*?)```', response, re.DOTALL).group(1)
        self.code_data.code = code
        return code

    def save_code(self, name: str) -> str:
        """
        Saves the generated code to the user's computer.

        :param str name: The name of the file to save the code.
        """
        path = os.path.join(PROJECT_PATH, f"{name}.js")
        self.code_data.name = name
        self.code_data.path = path
        with open(path, 'w') as file:
            file.write(self.code)
        return "Code saved successfully."

    def run_code(self) -> str:
        """
        Runs the generated code to start the project.
        """
        creation_result = subprocess.run(
            ["yarn", "create", "react-app", self.code_data.name],
            cwd=self.code_data.path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        with open(os.path.join(self.code_data.path, "src", "App.js"), 'w') as file:
            file.write(self.code_data.code)
        installation_result = subprocess.run(
            ["yarn", "install"],
            cwd=self.code_data.path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        starting_result = subprocess.run(
            ["yarn", "start"],
            cwd=self.code_data.path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
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
