from ..sql_type import SQLType


class Integer(SQLType):
    """INTEGER SQL type"""

    def __init__(self, autoincrement: bool = False):
        self.autoincrement = autoincrement

    def __repr__(self):
        return f"INTEGER{' AUTOINCREMENT' if self.autoincrement else ''}"
