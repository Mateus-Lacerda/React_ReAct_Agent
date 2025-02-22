[![Linter: Ruff](https://img.shields.io/badge/Linter-Ruff-brightgreen?style=flat-square)](https://github.com/charliermarsh/ruff)
# React ReAct Agent

React ReAct Agent is an agent-driven project designed to streamline the creation and execution of React applications using the ReAct methodology.

## Overview

This project leverages a single agent powered by three distinct prompts:
- A code generation prompt that builds React projects with a focus on responsiveness and appealing design.
- A system prompt that manages the agent’s behavior.
- A README summarization prompt that extracts key details from GitHub repositories.

The agent performs the following steps:
- Gather project ideas and additional details.
- Generate code based on the provided project summary.
- Save and run the generated code to launch the React project.

## How It Works

1. **Project Description**: The user describes the project idea (e.g., "Build a portfolio website").
2. **Information Gathering**: The agent asks follow-up questions to collect additional details (e.g., site sections, purpose, etc.).
3. **Code Generation**: The agent generates code using the three prompts.
4. **Saving & Running Code**: The generated code is saved as a JavaScript file (e.g., using `save_code`) and then executed (`run_code`) to start the project.

## Key Functions & Tools

- **save_code**: Saves the generated code to the user's computer by accepting a file name.
- **run_code**: Executes the saved JavaScript code to launch the React project.
- **make_code**: Generates the code based on the project summary and additional details.

## Getting Started

1. Ensure you have Python and Node.js installed.
2. Configure your environment as needed.
3. Run the main Python script to start the agent interaction.
4. Follow the prompts to describe your project, answer follow-up questions, and let the agent handle the rest.

## Directory Structure

```
/fast_camp_agents_2
├── src
│   ├── python
│   │   ├── agent
│   │   │   ├── prompt.py             // Contains prompt definitions for the agent
│   │   │   ├── react_react_agent.py  // Agent implementation for React projects with ReAct
│   │   │   └── tools.py              // Tool definitions used by the agent (e.g., save_code, run_code)
│   │   ├── models
│   │   │   └── code.py               // pydantic model to store the generated React code
│   └── utils
│         ├── colors.py               // Module for colored printing
│         ├── printer.py              // Module for printing messages
│         └── search_tool.py          // Module for search functionality
└── README.md
```

## CLI Usage
The command-line interface (CLI) lets you directly interact with the React ReAct Agent. For example, you can run the agent with:
```
python src/main.py --groq_api_key="your_groq_api_key" --github_access_token="your_github_token" --starting_prompt="Your prompt message" [--verbose]
```
Parameters:
- --groq_api_key (-gk): Specify your Groq API key.
- --github_access_token (-gh): Provide your Github access token.
- --starting_prompt (-p): Set the initial prompt for your interaction.
- --verbose (-v): Enable verbose mode for additional logging.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

---

Happy coding!
