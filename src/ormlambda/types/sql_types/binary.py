from typing import Optional
from ..sql_type import SQLType

class Binary(SQLType):
    """BINARY/VARBINARY/BLOB SQL type for bytes data in MySQL"""

    def __init__(self, length: Optional[int] = None, fixed_length: bool = False):
        """
        Initialize a Binary type
        
        Args:
            length: Maximum length in bytes, None for BLOB
            fixed_length: If True, uses BINARY (fixed length), otherwise VARBINARY (variable length)
        """
        super().__init__()
        self.length = length
        self.fixed_length = fixed_length

    def __repr__(self):
        if self.length is None:
            return "BLOB"
        elif self.fixed_length:
            return f"BINARY({self.length})"
        else:
            return f"VARBINARY({self.length})"
