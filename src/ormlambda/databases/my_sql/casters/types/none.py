from types import NoneType
from .base_write import IWrite
from .base_read import IRead


class MySQLWriteNoneType(IWrite[NoneType]):
    @staticmethod
    def cast(value: NoneType):
        return "NULL"


class MySQLReadNoneType(IRead[NoneType]):
    @staticmethod
    def cast(value: str) -> NoneType:
        return None
