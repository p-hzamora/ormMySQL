from typing import Literal, override, Callable
from orm.dissambler.tree_instruction import TreeInstruction
from orm.interfaces.IQuery import IQuery

import dis

ASC = "ASC"
DESC = "DESC"


class OrderQuery[T](IQuery):
    ORDER = "ORDER BY"

    def __init__(self, order_lambda: Callable[[T], None], order_type: Literal["ASC", "DESC"]) -> None:
        if not self._valid_order_type(order_type):
            raise Exception("order_type only can be 'ASC' or 'DESC'")

        self._order_lambda: Callable[[T], None] = order_lambda
        self._order_type: str = order_type
        self._column: str = TreeInstruction(dis.Bytecode(order_lambda), "tuple").to_list()[0].nested_element.name

    def _valid_order_type(self, _value: str) -> bool:
        return _value in (ASC, DESC)

    @override
    @property
    def query(self) -> str:
        return f"{self.ORDER} {self._column} {self._order_type}"
