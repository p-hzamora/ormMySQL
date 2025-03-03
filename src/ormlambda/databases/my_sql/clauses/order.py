from __future__ import annotations
import typing as tp

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext, ClauseContextType
from ormlambda.sql.types import ColumnType
from ormlambda.sql.clause_info import AggregateFunctionBase

from ormlambda.statements import OrderType


class Order(AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "ORDER BY"

    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp], ...] | ColumnType[TProp],
        order_type: tp.Iterable[OrderType],
        context: ClauseContextType = None,
    ):
        super().__init__(
            table=None,
            column=column,
            context=context,
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

    @tp.override
    @property
    def query(self) -> str:
        string_columns: list[str] = []
        columns = self.unresolved_column

        # if this attr is not iterable means that we only pass one column without wrapped in a list or tuple
        if not isinstance(columns, tp.Iterable):
            columns = (columns,)
        assert len(columns) == len(self._order_type)

        context = ClauseInfoContext(table_context=self._context._table_context, clause_context=None) if self._context else None
        for index, clause in enumerate(self._convert_into_clauseInfo(columns, context)):
            clause.alias_clause = None
            string_columns.append(f"{clause.query} {self._order_type[index].value}")

        return f"{self.FUNCTION_NAME()} {', '.join(string_columns)}"
