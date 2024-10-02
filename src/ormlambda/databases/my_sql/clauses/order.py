from typing import override, Callable

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.common.interfaces.IStatements import OrderType

ASC = "ASC"
DESC = "DESC"


class OrderQuery[T](IQuery):
    ORDER = "ORDER BY"

    def __init__(self, instance: T, order_lambda: Callable[[T], None], order_type: OrderType) -> None:
        if not self._valid_order_type(order_type):
            raise Exception("order_type only can be 'ASC' or 'DESC'")

        self._instance: T = instance
        self._order_lambda: Callable[[T], None] = order_lambda
        self._order_type: str = order_type
        self._column: str = TreeInstruction(order_lambda).to_list()[0].nested_element.name

    def _valid_order_type(self, _value: str) -> bool:
        return _value in (ASC, DESC)

    @override
    @property
    def query(self) -> str:
        return f"{self.ORDER} {self._instance.__table_name__}.{self._column} {self._order_type}"
