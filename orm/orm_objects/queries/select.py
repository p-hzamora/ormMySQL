from typing import Callable, Optional, Iterable, Type
import dis

from orm.dissambler import NestedElement
from orm.orm_objects import Table

from .query import IQuery
from orm.dissambler import TreeInstruction, TupleInstruction


class SelectQuery[T: Table](IQuery):
    def __init__(
        self,
        table: T,
        select_list: Optional[Callable[[T], None]] = lambda: None,
    ) -> None:
        self._table: T = table
        self._select_list: Iterable[str] = self._make_column_list(select_list)
        self._different_columns: Iterable[Table] = []

    def _make_column_list(self, select_list: Optional[Callable[[T], None]]) -> Iterable[str]:
        instruction_list: list[TupleInstruction] = TreeInstruction(dis.Bytecode(select_list), list).to_list()

        res = []
        obj: Type[T] = self._table
        for tuple_instruction in instruction_list:
            last_nested_element: str = tuple_instruction.nested_element.name
            if hasattr(obj, tuple_instruction.nested_element.name):
                value: Table | property = getattr(obj, last_nested_element)

                if isinstance(value, property):  # if is property we gonna get column of the initial table
                    res.append(f"{obj.__table_name__}.{last_nested_element}")

                elif issubclass(value, Table):
                    for children in tuple_instruction.nested_element.parents:
                        if hasattr(value, children):
                            ...
                    res.append(f"{value.__table_name__}.*")
                else:
                    raise Exception
            else:
                external_table: str = self._get_parent_table_name(self._table, tuple_instruction.nested_element.parents[1:])
                res.append(f"{external_table}.{tuple_instruction.nested_element.name}")

        return res

    @classmethod
    def _get_parent_table_name(cls, table: Type[Table], nested_string: list[str]) -> str:
        for name in nested_string:
            if hasattr(table, name):
                new_table: Table | property = getattr(table, name)
                # To avoid confusion, ensure that column names and table names are clearly distinct.
                if not isinstance(new_table, property):
                    new_nested_string = nested_string[nested_string.index(name) + 1 :]
                    return cls._get_parent_table_name(new_table, new_nested_string)
            return table.__table_name__

    def _convert_select_list(self) -> str:
        if not self._select_list:
            return "*"
        else:
            return ", ".join(self._select_list)

    @property
    def query(self) -> str:
        select_str = self._convert_select_list()
        query = f"SELECT {select_str} FROM {self._table.__table_name__}"
        return query
