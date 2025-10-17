from ormlambda import Column, Table
from ormlambda import DECIMAL, DATE, DATETIME, POINT, INT, VARCHAR, FLOAT


from typing import TypedDict


class ResponseJson(TypedDict):
    new_value: int
    is_valid: bool
    errors: list[int]


class TableType(Table):
    __table_name__ = "table_type"

    pk: Column[INT] = Column(INT(), is_primary_key=True, is_auto_increment=False)
    strings: Column[VARCHAR] = Column(VARCHAR(255))
    integers: Column[INT] = Column(INT())
    floats: Column[FLOAT] = Column(FLOAT())
    points: Column[POINT] = Column(POINT())
    datetimes: Column[DATETIME] = Column(DATETIME())
    dates: Column[DATE] = Column(DATE())
    decimals: Column[DECIMAL] = Column(DECIMAL(precision=5, scale=2))
    jsons: Column[ResponseJson]
