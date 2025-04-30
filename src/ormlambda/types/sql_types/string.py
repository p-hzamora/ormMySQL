from typing import Optional
from ..sql_type import SQLType


class String(SQLType):
    """VARCHAR SQL type"""

    def __init__(self, length: Optional[int] = None):
        super().__init__()
        self.length = length

    def __repr__(self):
        return f"VARCHAR({self.length})" if self.length else "VARCHAR"
