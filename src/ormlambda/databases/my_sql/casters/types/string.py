from .base_write import IWrite
from .base_read import IRead


class MySQLWriteString(IWrite[str]):
    @staticmethod
    def cast(value: str):
        return f"'{value}'"


class MySQLReadString(IRead[str]):
    @staticmethod
    def cast(value: str) -> str:
        return str(value)
