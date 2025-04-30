from typing import Optional
from ..sql_type import SQLType


class Timestamp(SQLType):
    """TIMESTAMP SQL type"""

    def __init__(self, timezone: bool = False, precision: Optional[int] = None):
        self.timezone = timezone
        self.precision = precision

    def __repr__(self):
        return "TIMESTAMP"
