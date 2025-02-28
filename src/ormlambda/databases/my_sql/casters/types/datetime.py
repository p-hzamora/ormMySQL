from datetime import datetime

from ormlambda.caster import PLACEHOLDER


from .base_write import IWrite
from .base_read import IRead
# from .string import MySQLWriteString


class MySQLWriteDatetime(IWrite[datetime]):
    def cast(value: datetime, insert_data: bool = False) -> str:
        if value == PLACEHOLDER:
            return value

        # str_datetime: str = value.strftime("%Y-%m-%d %H:%M:%S")
        return value
        # return MySQLWriteString.cast(str_datetime)


class MySQLReadDatetime(IRead[datetime]):
    @staticmethod
    def cast(value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
