from __future__ import annotations
import typing as tp

from ormlambda.sql.functions.interface import IFunction
from ormlambda.sql.types import ColumnType

from ormlambda.common.enums import OrderType
from ormlambda.sql.elements import ClauseElement

if tp.TYPE_CHECKING:
    from ormlambda import ColumnProxy


class Order[TProp](ClauseElement, IFunction):
    __visit_name__ = "order"

    columns: tuple[ColumnType[TProp], ...]

    def __init__(
        self,
        *columns: ColumnProxy[TProp],
        order_type: tp.Iterable[OrderType],
    ):
        if isinstance(columns, str) or not isinstance(columns, tp.Iterable):
            columns = (columns,)

        if isinstance(order_type, str) or not isinstance(order_type, tp.Iterable):
            order_type = (order_type,)

        self.columns = columns
        self._order_type: list[OrderType] = [self.__cast_to_OrderType(x) for x in order_type]

    def __cast_to_OrderType(self, _value: tp.Any) -> tp.Iterable[OrderType]:
        if isinstance(_value, OrderType):
            return _value

        if isinstance(_value, str):
            try:
                return OrderType(_value)
            except Exception:
                pass
        raise Exception(f"order_type param only can be 'ASC' or 'DESC' string or '{OrderType.__name__}' enum")

    def used_columns(self):
        return self.columns

    @property
    def dtype(self) -> tp.Any: ...


__all__ = ["Order"]
