"""Module for the search tools."""
import base64
import os

import requests

from .printer import print_function_message

def make_gh_authed_request(url: str) -> requests.Response:
  """
  Makes an authenticated request to the github API.
  """
  headers = {
      "User-Agent": "React-ReAct-Agent",
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {os.getenv('GH_TOKEN')}"
  }
  response = requests.get(url, headers=headers, timeout=20)
  return response

def search_github(url: str, verbose: bool = False) -> list:
    """
    Searches the user's github pages.

    Parameters:
        url (str): The user's github url.
    Returns:
        list: The repos README.md files, if exists in branch main.
    """
    response = make_gh_authed_request(url)
    results = []
    if response.status_code == 200:
        result = response.json()
        print_function_message(f"{len(result)} repositories found.", verbose=verbose)
        for item in result:
            contents_url = item.get('url')
            if contents_url:
                readme_path = f"{contents_url}/readme"
                try:
                    readme_response = make_gh_authed_request(readme_path)
                except requests.exceptions.Timeout:
                    print_function_message(f"Timeout error on url: {readme_path}.", verbose=verbose)
                    continue
                if readme_response.status_code == 200:
                    print_function_message(f"README.md found in {item.get('name')}.", verbose=verbose)
                    readme = readme_response.json()
                    content = base64.b64decode(readme.get('content')).decode('utf-8')
                    results.append(content)
    return results
