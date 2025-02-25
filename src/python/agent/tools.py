TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_github_pages",
            "description": "Searches the user's github pages",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The user's github username. Ask him before using this tool."
                    }
                },
                "required": ["username"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_info",
            "description": "Stores the user's information",
            "parameters": {
                "type": "object",
                "properties": {
                    "info": {
                        "type": "string",
                        "description": "The information to store"
                    }
                },
                "required": ["info"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_code",
            "description": "Calling this tool generates the code for the project using the stored information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_summary": {
                        "type": "string",
                        "description": "The summary of the project. Make it simple."
                    },
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project."
                    }
                },
                "required": ["project_summary", "project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Runs the generated code to start the project.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

EDIT_CODE_TOOL = {
    "type": "function",
    "function": {
        "name": "edit_code",
        "description": "Edits the generated code.",
        "parameters": {
            "type": "object",
            "properties": {
                "changes": {
                    "type": "string",
                    "description": "The changes to be made in the code."
                }
            },
        }
    }
}