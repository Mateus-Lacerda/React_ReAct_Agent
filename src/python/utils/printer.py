"""Class for printing utilities"""
from .colors import Colors as cl

def print_assistant_message(message: str) -> None:
    """Prints the assistant message."""
    print(cl.colored(f"Assistant: {message}", 'BLUE'))

def print_function_message(message: str, verbose: bool = False) -> None:
    """Prints the function message."""
    if verbose:
        print(cl.colored(f"Function: {message}", 'YELLOW'))
