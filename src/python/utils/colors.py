"""Class for colored text in terminal"""
from dataclasses import dataclass

@dataclass
class Colors:
    """Class for colored text in terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    @classmethod
    def colored(__class__, text: str, color: str) -> str:
        """Return colored text."""
        return f"{getattr(__class__, color)}{text}{__class__.ENDC}"
