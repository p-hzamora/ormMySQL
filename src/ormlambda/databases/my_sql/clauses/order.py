from __future__ import annotations
from typing import override, Callable, TYPE_CHECKING, Any, Iterable

from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo


if TYPE_CHECKING:
    from ormlambda import Table

from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
from ormlambda.common.interfaces.IStatements import OrderType


class OrderQuery[T: Table](DecompositionQueryBase[T]):
    ORDER = "ORDER BY"

    def __init__[*Ts](self, instance: T, lambda_query: Callable[[Any], tuple[*Ts]], order_type: Iterable[OrderType]) -> None:
        super().__init__(instance, lambda_query)

        if isinstance(order_type, str) or not isinstance(order_type, Iterable):
            order_type = (order_type,)

        self._order_type: list[OrderType] = [self.__cast_to_OrderType(x) for x in order_type]

    def __cast_to_OrderType(self, _value: Any) -> Iterable[OrderType]:
        if isinstance(_value, OrderType):
            return _value

        if isinstance(_value, str):
            try:
                return OrderType(_value)
            except Exception:
                pass
        raise Exception(f"order_type param only can be 'ASC' or 'DESC' string or '{OrderType.__name__}' enum")

    def alias_children_resolver[Tclause](self, clause_info: ClauseInfo[Tclause]):
        return None

    @override
    @property
    def query(self) -> str:
        assert len(self.all_clauses) == len(self._order_type)

        query: list[str] = []
        for index, x in enumerate(self.all_clauses):
            query.append(f"{x.query} {self._order_type[index].value}")
        return f"{self.ORDER} {", ".join(query)}"
