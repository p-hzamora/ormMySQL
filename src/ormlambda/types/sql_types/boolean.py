from ..sql_type import SQLType


class Boolean(SQLType):
    """BOOLEAN SQL type"""

    def __repr__(self):
        return "BOOLEAN"
