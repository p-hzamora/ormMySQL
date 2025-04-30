from ..sql_type import SQLType


class Char(SQLType):
    """CHAR SQL type"""

    def __init__(self, length: int = 1):
        super().__init__()
        self.length = length

    def __repr__(self):
        return f"CHAR({self.length})"
