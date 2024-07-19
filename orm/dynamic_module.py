import sys
from pathlib import Path
from typing import Optional, Type
import re

from .orm_objects.table import Table
from .orm_objects.foreign_key import ForeignKey

import importlib
import inspect


class Node:
    pattern: str = r"from \.(\w+) import (\w+)"

    def __init__(
        self,
        file: str | Path,
        relative_path: str | Path,
        class_name: str = None,
        fks: list[str, str] = None,
    ):
        self._file: Path = self._set_paths(file)
        self._relative_path: Path = self._set_paths(relative_path)
        self._class_name: str = class_name
        self._fks: list[str, str] = fks

        self._relative_modules: list["Node"] = self.extract_modules()

    def __repr__(self) -> str:
        return f"Module: {self.module_name}, class: {self.class_name} ->({Node.__name__})"

    def __eq__(self, __value: "Node") -> bool:
        return hash(__value) == hash(self)

    def __hash__(self) -> int:
        return hash(
            (
                self.class_name,
                self.code,
            )
        )

    def _validate_paths(self, path: Path | str) -> bool:
        if isinstance(path, str):
            return Path(path).exists()
        return path.exists()

    def _set_paths(self, path: str | Path):
        if not self._validate_paths(path):
            raise OSError(path)
        return Path(path).resolve()

    def extract_modules(self) -> list["Node"]:
        if self._fks:
            rel_modules: list[tuple[str, str]] = self._fks
        else:
            rel_modules: list[tuple[str, str]] = re.findall(self.pattern, self.code) if self._file is not None else []

        if not rel_modules:
            return []
        return [
            Node(
                file=self._relative_path.joinpath(module_).with_suffix(".py"),
                relative_path=self._relative_path,
                class_name=class_,
            )
            for module_, class_ in rel_modules
        ]

    @property
    def code(self) -> str:
        if not self._file:
            return None
        return self._file.read_text()

    @property
    def file(self) -> Path:
        return self._file

    @property
    def class_name(self) -> str:
        if not self._class_name:
            pattern = re.compile(r"class\s(\w+)\(.*Table.*\):")

            condition = pattern.search(self.code)
            if condition:
                self._class_name = condition.group(1)
                return self.class_name
            return None
        return self._class_name

    @property
    def module_name(self) -> str:
        return self._file.stem

    @property
    def relative_modules(self) -> list["Node"]:
        return self._relative_modules

    @relative_modules.setter
    def relative_modules(self, value: list):
        self._relative_modules = value

    @property
    def is_dependent(self) -> bool:
        return len(self.relative_modules) > 0


class ModuleTree:
    def __init__(self, module_path: Path) -> None:
        if isinstance(module_path, str):
            module_path = Path(module_path)

        self.module_path: Path = module_path
        self.order_module_tuple: tuple[Node, ...] = self.get_order_module_tuple_from_path()

    def get_order_module_tuple_from_path(self) -> tuple[Node]:
        if self.module_path.is_dir():
            return self.order_modules_from_folder()
        return self.order_modules_from_file()

    def order_modules_from_folder(self) -> tuple[Node]:
        """
        Method whose main used is sorting all .py inside of folder to avoid import errors and overall for the creation of tables in SQL, comply with foreign key referenced table
        This method's main purpose is to sort all .py inside a folder to avoid import errors and to ensure that tables referenced by foreign key in other tables are created first
        """
        order_list: list[Node] = []
        unorder_module_list: list[Node] = []

        for p in self.module_path.iterdir():
            if not p.is_dir():
                unorder_module_list.append(Node(file=p, relative_path=self.module_path))

        self.sort_dicc(unorder_module_list, order_list)
        return tuple(order_list)

    @staticmethod
    def sort_dicc(list_nodes: list[Node], new_list: list[Node]) -> None:
        """
        Iterated throughout list_nodes var and feed 'new_list' mutable var

        Must create a mutable object such as list, to fill it with ordered items
        """

        def add_children(list_nodes: list[Node], new_list: list[Node], node: Node):
            """
            Recursive method called when try to sort all Nodes

            ARGUMENT
            -

                - list_nodes: list[Node]
                - new_list:list[Node]
            """
            all_children_added = all(x in new_list for x in node.relative_modules)

            if node not in new_list and node._file is not None and ((node.is_dependent and all_children_added) or not node.is_dependent):
                new_list.append(node)
                return None

            if node in new_list and not node.is_dependent:
                return None

            for child_node in node.relative_modules:
                add_children(list_nodes, new_list, child_node)

        for node in list_nodes:
            if node not in new_list and all([child_node in new_list for child_node in node.relative_modules]):
                new_list.append(node)

            add_children(list_nodes, new_list, node)
        return None

    def order_modules_from_file(self) -> tuple[Node]:
        """
        Method whose main used is sorting all .py inside of folder to avoid import errors and overall for the creation of tables in SQL, comply with foreign key referenced table
        This method's main purpose is to sort all .py inside a folder to avoid import errors and to ensure that tables referenced by foreign key in other tables are created first
        """
        # FIXME [ ]: wip. Must be create a way to order all models when that classes are in the same file
        # order_list: list[Node] = []
        unorder_module_list: list[Node] = []

        tables: list[tuple[str, Table]] = self.get_member_table(self.load_module("", self.module_path))

        for table_name, table_obj in tables:
            fks = ForeignKey.get_fk_from_table(table_obj)
            if not fks:
                fks = []
            else:
                for _, lista in fks.items():
                    unorder_module_list.append(
                        Node(
                            self.module_path,
                            relative_path=self.module_path,
                            class_name=table_name,
                            fks=[(self.module_path, x.__name__) for x in lista],
                        )
                    )
        # FIXME [ ]: It's Broken. If test 'test_create_table_code_first_passing_file' passes, it's by CHANCE and we should not consider ti as valid
        # self.sort_dicc(unorder_module_list, order_list)
        return tuple(unorder_module_list[::-1])

    @staticmethod
    def find_module(module_name: str, nodes: list["Node"]) -> Optional["Node"]:
        for node in nodes:
            if module_name == node.class_name:
                return node
        return None

    @staticmethod
    def load_module(module_name: str, module_path: Path):
        """
        Method whose main purpose is the dynamic addtion of modules using the importlib module.
        Both the module name and its path must be specified.

        !important: we need to add the dynamic modules to sys.modules for the loading to be successful
        """
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def get_tables(self) -> tuple[str, Type[Table]]:
        table_list: list[Table] = []
        for node in self.order_module_tuple:
            # avoid __init__ because we can get relative import not found error
            if node.file.is_dir() or node.class_name == "__init__":
                continue

            # loop over order modules tuple to load it into sys.modules
            submodule = self.load_module(f"{self.module_path.stem}.{node.class_name}", node.file)
            table_class = self.get_member_table(submodule)

            # we need to ensure that the object we going to add in table_list is the same
            for name, obj in table_class:
                if name == node.class_name:
                    table_list.append(obj)
        return tuple(table_list)

    @staticmethod
    def get_member_table(module) -> list[tuple[str, Type[Table]]]:
        return inspect.getmembers(module, lambda x: inspect.isclass(x) and issubclass(x, Table) and x is not Table)
