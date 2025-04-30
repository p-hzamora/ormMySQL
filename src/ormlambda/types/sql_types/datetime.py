from typing import Optional
from ..sql_type import SQLType


class DateTime(SQLType):
    """DATETIME SQL type"""

    def __init__(self, precision: Optional[int] = None):
        self.precision = precision

    def __repr__(self):
        return "DATETIME"
