from ormlambda.caster import PLACEHOLDER
from .base_write import IWrite
from .base_read import IRead


class MySQLWriteString(IWrite[str]):
    @staticmethod
    def cast(value: str, insert_data: bool = False) -> str:
        if value == PLACEHOLDER:
            return value
        return str(value)


class MySQLReadString(IRead[str]):
    @staticmethod
    def cast(value: str) -> str:
        return str(value)
