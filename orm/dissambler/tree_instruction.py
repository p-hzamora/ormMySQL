from collections import defaultdict
from typing import Self, Optional, Literal
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

    def __repr__(self) -> str:
        return f"{TreeInstruction.__name__} < at {hex(id(self))}>"

    @classmethod
    def _valid_dtype(cls, dtype: object) -> OpName:
        for key, values in cls._VALID_DTYPES.items():
            if dtype in values:
                return key

    def create(self) -> dict[str, list[NestedElement[str]]]:
        for x in self._bytecode:
            self._raise_error_if_not_valid(x)
            self.add_instruction(x)

        dicc: dict[str, list[NestedElement[str]]] = defaultdict(list)
        for node in self.root.children:
            lista = self.get_all_nodes_of(node)

            # We just want to retrieve argval not Instruction object itself
            argval_list = [x.data.argval for x in lista]
            dicc[node.data.argval].append(NestedElement[str](argval_list))

        return dicc

    def _raise_error_if_not_valid(self, ins: Instruction) -> bool:
        if self._dtype != OpName.COMPARE_OP and OpName(ins.opname) == OpName.COMPARE_OP:
            raise ValueError(f"Comparable symbols does not expected when '{self._dtype}' is specified.\nTry passing 'COMPARABLE' as type parameter")

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

    @property
    def root(self) -> Node[Instruction]:
        return self._root
