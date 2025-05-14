from typing import Optional
from ..sql_type import SQLType


class TEXT(SQLType):
    """TEXT SQL type"""

    def __init__(self, size: Optional[str] = None):
        self.size = size

    def __repr__(self):
        return "TEXT"
