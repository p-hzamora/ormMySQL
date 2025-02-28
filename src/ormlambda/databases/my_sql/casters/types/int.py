from .base_write import IWrite
from .base_read import IRead


class MySQLWriteInt(IWrite[int]):
    @staticmethod
    def cast(value: int, insert_data: bool = False) -> str:
        return str(value)


class MySQLReadInt(IRead[int]):
    @staticmethod
    def cast(value: str) -> int:
        return int(value)
