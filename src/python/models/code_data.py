"""Module for the code data model."""
from pydantic import BaseModel

class CodeData(BaseModel):
    """The code data model."""
    code: str | None = None
    name: str | None = None
    path: str | None = None
