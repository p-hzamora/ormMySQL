from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info.clause_info_context import ClauseContextType
from ormlambda.sql.types import ColumnType
from ormlambda.sql.clause_info import AggregateFunctionBase

from ormlambda.statements import OrderType
from ormlambda.sql.elements import ClauseElement

if tp.TYPE_CHECKING:
    from ormlambda.dialects import Dialect


class Order(AggregateFunctionBase, ClauseElement):
    __visit_name__ = "order"

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "ORDER BY"

    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp], ...] | ColumnType[TProp],
        order_type: tp.Iterable[OrderType],
        context: ClauseContextType = None,
        *,
        dialect: Dialect,
        **kw,
    ):
        super().__init__(
            table=None,
            column=column,
            context=context,
            dialect=dialect,
            **kw,
        )

        if isinstance(order_type, str) or not isinstance(order_type, tp.Iterable):
            order_type = (order_type,)

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

__all__ = ["Order"]
