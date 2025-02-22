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
                        "description": "The user's github username. Must be only a string value!"
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
            "description": "Generates the code for the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "idea": {
                        "type": "string",
                        "description": "The idea for the project"
                    }
                },
                "required": ["idea"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_code",
            "description": "Saves the generated code to the user's computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to save the code. Must be only a string value!"
                    }
                },
                "required": ["name"]
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
    },
]
