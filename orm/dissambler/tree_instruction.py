from collections import defaultdict
from typing import Any, NamedTuple, Self, Optional, Literal
from dis import Instruction, Bytecode
from .dis_types import OpName
from .nested_element import NestedElement


class Node[T]:
    def __init__(self, data: T):
        self.data: T = data
        self.children: list[Self[T]] = []

    def __repr__(self) -> str:
        return f"{Node.__name__}: data={self.data} children={self.children}"


DTypes = Literal[
    "tuple",
    "list",
    "dict",
    "set",
    "COMPARABLE",
]


class TupleInstruction(NamedTuple):
    var: str
    nested_element: NestedElement[str]


class TreeInstruction:
    _FIRST_LEVEL: tuple[OpName] = (
        OpName.LOAD_FAST,
        OpName.LOAD_GLOBAL,
        OpName.LOAD_CONST,
    )

    _VALID_DTYPES: dict[object, OpName] = {
        OpName.BUILD_TUPLE: (tuple, "tuple"),
        OpName.BUILD_LIST: (list, "list"),
        OpName.BUILD_MAP: (dict, "dict"),
        OpName.BUILD_SET: (set, "set"),
        OpName.COMPARE_OP: ("COMPARABLE",),
    }

    def __init__(self, byte_code: Bytecode, dtype: object | DTypes):
        self._root: Node[Instruction] = Node[Instruction](None)
        self._bytecode: Bytecode = byte_code
        self._dtype: OpName = self._valid_dtype(dtype)
        self._compare_op: Optional[str] = None
        self._set_root()

    def __repr__(self) -> str:
        return f"{TreeInstruction.__name__} < at {hex(id(self))}>"

    @classmethod
    def _valid_dtype(cls, dtype: object | DTypes) -> OpName:
        for key, values in cls._VALID_DTYPES.items():
            if dtype in values:
                return key

    def _set_root(self) -> None:
        """
        add instructions into self._root
        """
        for x in self._bytecode:
            if OpName(x.opname) == OpName.COMPARE_OP:
                self._compare_op = x.argval
            self._raise_error_if_not_valid(x)
            self.add_instruction(x)

    def to_dict(self) -> dict[str, list[NestedElement[str]]]:
        _dict: dict[str, list[NestedElement[str]]] = defaultdict(list)
        for node in self.root.children:
            argval = self._join_data_attributes_from_node(node)
            _dict[node.data.argval].append(NestedElement[str](argval))
        return _dict

    def _raise_error_if_not_valid(self, ins: Instruction) -> bool:
        if self._dtype != OpName.COMPARE_OP and OpName(ins.opname) == OpName.COMPARE_OP:
            raise ValueError(f"Comparable symbols does not expected when '{self._dtype}' is specified.\nTry passing '{self._VALID_DTYPES[OpName.COMPARE_OP]}' as type parameter")

    def add_instruction(self, ins: Instruction) -> None:
        opname = OpName(ins.opname)
        if opname in TreeInstruction._FIRST_LEVEL:
            self._root.children.append(Node[Instruction](ins))
            return None

        if OpName(ins.opname) == OpName.LOAD_ATTR:
            last_fast_node = self._root.children[-1]
            new_node = Node[Instruction](ins)
            self._add_node(last_fast_node, new_node)
        return None

    def _add_node(self, parent_node: Node[Instruction], new_node: Node[Instruction]):
        parent_node.children.append(new_node)
        return None

    def get_all_nodes_of(self, node: Node[Instruction]) -> list[Node[Optional[Instruction]]]:
        def get_all_nodes(node: Node[Instruction], list: list[Node[Instruction]]):
            if not node.children:
                return list
            for subnode in node.children:
                if not subnode.children:
                    data = subnode
                else:
                    data = self.get_all_nodes_of(subnode)
                list.append(data)

        lista = []
        get_all_nodes(node, lista)
        return lista

    def to_list(self) -> list[TupleInstruction]:
        _list: list[list[NestedElement[str]]] = []
        for node in self.root.children:
            argval = self._join_data_attributes_from_node(node)
            _list.append(TupleInstruction(node.data.argval, NestedElement[str](argval)))
        return _list

    def _join_data_attributes_from_node(self, _node: Node[Instruction]) -> list[Any]:
        lista = self.get_all_nodes_of(_node)
        if not lista:
            return _node.data.argval
        else:
            # We just want to retrieve argval not Instruction object itself
            return [_node.data.argval] + [x.data.argval for x in lista]

    @property
    def root(self) -> Node[Instruction]:
        return self._root

    @property
    def compare_op(self) -> Optional[str]:
        return self._compare_op
