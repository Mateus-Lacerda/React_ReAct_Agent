"""Starts the React ReAct agent application."""
import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dotenv import load_dotenv

from python.agent.react_react_agent import ReactReActAgent
from python.utils.colors import Colors as cl

def load_env() -> None:
    """Loads the environment variables."""
    load_dotenv('.env.local')
    if not os.getenv('PROJECT_PATH'):
        raise ValueError('PROJECT_PATH environment variable not found.')
    if not os.getenv('GROK_API_KEY'):
        raise ValueError('GROK_API_KEY environment variable not found.')
    if not os.getenv('GH_TOKEN'):
        raise ValueError('GH_TOKEN environment variable not found.')

if __name__=='__main__':
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"""
{cl.colored("Starts the React ReAct agent application.", 'BLUE')}
---
{cl.colored("First, create a .env.local file in the root directory with the following environment variables:", 'YELLOW')}
{cl.colored("PROJECT_PATH=<your_react_project_path>", 'GREEN')}, {cl.colored("highly recommended to be placed inside the 'src' directory.", 'RED')}
{cl.colored("GROK_API_KEY=<your_grok_api_key>", 'GREEN')}
        """.strip()
        )
    parser.add_argument('--grok_api_key', '-gk', type=str, help='The Grok API key.')
    parser.add_argument('--github_access_token', '-gh', type=str, help='The Github access token.')
    parser.add_argument('--starting_prompt', '-p', type=str, help='The starting prompt for the agent.')
    parser.add_argument('--verbose', '-v', action='store_true', help='The verbose mode for the agent.')
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    if args.grok_api_key:
        if not os.path.exists('.env.local'):
            os.system('touch .env.local')

        os.system(f'echo "GROK_API_KEY={args.grok_api_key}" >> .env.local')
        print(cl.colored('GROK_API_KEY environment variable added to .env.local.', 'GREEN'))

    if args.github_access_token:
        if not os.path.exists('.env.local'):
            os.system('touch .env.local')

        os.system(f'echo "GH_TOKEN={args.github_access_token}" >> .env.local')
        print(cl.colored('GH_TOKEN environment variable added to .env.local.', 'GREEN'))

    if not os.path.exists('.env.local'):
        raise FileNotFoundError(
            '.env.local file notfound. Please create one with the necessary environment variables.'
            )
    else:
        load_env()

    if args.starting_prompt:
        verbose = False
        if args.verbose:
            verbose = True
        load_env()
        developer = ReactReActAgent(verbose=verbose)
        developer.chat(args.starting_prompt)

    else:
        print(cl.colored('Your environment is ready to start the React ReAct agent.', 'GREEN'))
        print(cl.colored('Run the following command to start the agent:', 'YELLOW'))
        print(cl.colored('python src/main.py --starting_prompt="Starting React ReAct agent..."', 'YELLOW'))
        sys.exit(0)
