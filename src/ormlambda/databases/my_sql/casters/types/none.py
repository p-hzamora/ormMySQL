from types import NoneType

from ormlambda.caster import PLACEHOLDER
from .base_write import IWrite
from .base_read import IRead


class MySQLWriteNoneType(IWrite[NoneType]):
    @staticmethod
    def cast(value: NoneType, insert_data: bool = False) -> str:
        if value == PLACEHOLDER:
            return value
        return "NULL"


class MySQLReadNoneType(IRead[NoneType]):
    @staticmethod
    def cast(value: str) -> NoneType:
        return None
