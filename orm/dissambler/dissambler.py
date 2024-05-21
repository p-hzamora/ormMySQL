import dis
from typing import Any, Callable, Generator, overload
from queue import Queue
from collections import defaultdict
from .dis_types import OpName
import inspect

from orm.condition_types import ConditionType



class Dissambler[TProp1, TProp2: Any]:
    __slots__ = (
        "_function",
        "_bytecode_function",
        "_cond_1",
        "_cond_2",
        "_compare_op",
        "_all_string_cond_1",
        "_all_string_cond_2",
    )

    @overload
    def __init__(self, function: Callable[[], bool]) -> None: ...

    @overload
    def __init__(self, function: Callable[[TProp1], bool]) -> None: ...

    @overload
    def __init__(self, function: Callable[[TProp1, TProp2], bool]) -> None: ...

    def __init__(self, function: Callable[[], bool] | Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool]) -> None:
        self._function: Callable[[], bool] | Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool] = function
        self._bytecode_function: Generator[dis.Instruction] = dis.get_instructions(function)
        self._all_string_cond_1:list[str] = []
        self._all_string_cond_2:list[str] = []
        self.__init_custom__()

    def __init_custom__(self):
        n_signature = len(inspect.signature(self._function).parameters)
        if n_signature == 0:
            self.__init__zero_attr()

        elif n_signature == 1:
            self.__init__one_attr()

        elif n_signature == 2:
            self.__init__two_attr()
        else:
            raise Exception(f"Number of arguments '{n_signature}' not expected.")

    def __init__zero_attr(self) -> None:
        load_const_queue = Queue()

        n_compare: list[int] = []
        for x in self._bytecode_function:
            self.__valid__compare_op(n_compare, x)

            if OpName(x.opname) == OpName.LOAD_CONST:
                load_const_queue.put(x.argval)

            if OpName(x.opname) == OpName.COMPARE_OP:
                self._compare_op: str = self._transform__compare_op(ConditionType(x.argval))

        self._cond_1 = load_const_queue.get_nowait()
        self._cond_2 = load_const_queue.get_nowait()
        return None

    def __init__one_attr(self) -> None:
        load_fast: dict[str, list[TProp1]] = defaultdict(list)
        n_compare: list[int] = []
        fast_var: list[str] = []
        load_consts: tuple[OpName] = (
            OpName.LOAD_CONST,
            OpName.LOAD_DEREF,
            OpName.LOAD_GLOBAL,
        )

        CONST_NAME = "const"
        for x in self._bytecode_function:
            op_name: OpName = OpName(x.opname)
            self.__valid__compare_op(n_compare, x)

            if op_name in load_consts:
                fast_var.append(CONST_NAME)
                load_fast[CONST_NAME].append(x.argval)

            if op_name == OpName.LOAD_FAST:
                fast_var.append(x.argval)
                load_fast[x.argval]

            if op_name == OpName.LOAD_ATTR:
                load_fast[fast_var[-1]].append(x.argval)

            if op_name == OpName.COMPARE_OP:
                self._compare_op: str = self._transform__compare_op(ConditionType(x.argval))


        self._cond_1: TProp1 = load_fast.pop(fast_var[0])[-1]
        self._cond_2: TProp2 = load_fast.pop(fast_var[1])[-1]
        return None

    def __init__two_attr(self) -> None:
        self.__init__one_attr()
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>: {self._cond_1} {self._cond_2} {self._compare_op} "

    @staticmethod
    def __valid__compare_op(n_compare: list[int], instruction: dis.Instruction) -> None:
        if OpName(instruction.opname) == OpName.COMPARE_OP:
            n_compare.append(1)
        if len(n_compare) > 1:
            raise ValueError(f"Must be only 'one condition' inside of lambda function.\n{instruction.argval}")

    @staticmethod
    def _transform__compare_op(compare_sybmol: ConditionType) -> str:
        dicc_symbols: dict[ConditionType, str] = {
            ConditionType.EQUAL: "=",
        }
        return dicc_symbols.get(compare_sybmol, compare_sybmol.value)

    @property
    def cond_1(self) -> Any:
        return self._cond_1

    @property
    def cond_2(self) -> Any:
        return self._cond_2

    @property
    def compare_op(self) -> str:
        return self._compare_op

    # @property
    # def parent(self):
    #     self._all_
