"""Module for the code data model."""
from pydantic import BaseModel

class CodeData(BaseModel):
    """The code data model."""
    code: str | None = None
    name: str | None = None
    path: str | None = None

    def is_complete(self) -> bool:
        """Checks if the code data is complete."""
        if any([self.code, self.name, self.path]):
            return True
        return False

class CodeStatus(BaseModel):
    """The code status model."""
    project_created: bool = False
    code_saved: bool = False
