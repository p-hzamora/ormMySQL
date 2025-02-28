from .base_write import IWrite
from .base_read import IRead

from .int import MySQLWriteInt


class MySQLWriteFloat(IWrite[float]):
    @staticmethod
    def cast(value: float, insert_data: bool = False) -> str:
        return MySQLWriteInt.cast(value)


class MySQLReadFloat(IRead[float]):
    @staticmethod
    def cast(value: str) -> float:
        return float(value)
