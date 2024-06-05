import dis
from typing import Any, Callable, overload

from orm.condition_types import ConditionType
from .nested_element import NestedElement
from .tree_instruction import TreeInstruction


class Dissambler[TProp1, TProp2: Any]:
    """
    class to dissambler lambda function to detach information from left to right of compare symbol.

    >>> dis = Dissambler[DtoC, None](lambda d: d.c.b.b_data == "asdf")

    >>> dis.cond_1.name # b_data
    >>> dis.cond_1.parent.parent.parent.name # d
    >>> dis.cond_1.parent.parent.name # c

    >>> dis.cond_2.name, "asdf"

    >>> dis.compare_op, "="

    """

    __slots__ = (
        "_function",
        "_bytecode_function",
        "_cond_1",
        "_cond_2",
        "_compare_op",
    )

    @overload
    def __init__(self, function: Callable[[], bool]) -> None: ...

    @overload
    def __init__(self, function: Callable[[TProp1], bool]) -> None: ...

    @overload
    def __init__(self, function: Callable[[TProp1, TProp2], bool]) -> None: ...

    def __init__(self, function: Callable[[], bool] | Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool]) -> None:
        self._function: Callable[[], bool] | Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool] = function
        self._bytecode_function: dis.Bytecode = dis.Bytecode(function)
        self.__init_custom__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>: {self._cond_1.name} {self._cond_2.name} {self._compare_op}"

    def __init_custom__(self):
        tree = TreeInstruction(dis.Bytecode(self._function), "COMPARABLE")
        dicc = tree.to_list()
        self._compare_op:str = self._transform__compare_op(ConditionType(tree.compare_op))

        self._cond_1: NestedElement[TProp1] = dicc[0].nested_element
        self._cond_2: NestedElement[TProp2] = dicc[1].nested_element

        return None

    @staticmethod
    def _transform__compare_op(compare_sybmol: ConditionType) -> str:
        dicc_symbols: dict[ConditionType, str] = {
            ConditionType.EQUAL: "=",
        }
        return dicc_symbols.get(compare_sybmol, compare_sybmol.value)

    @property
    def cond_1(self) -> NestedElement[str]:
        return self._cond_1

    @property
    def cond_2(self) -> NestedElement[str]:
        return self._cond_2

    @property
    def compare_op(self) -> str:
        return self._compare_op
