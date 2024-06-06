from typing import Callable, Optional, Iterable
import dis

import inspect
from orm.dissambler import NestedElement
from orm.orm_objects import Table
from orm.orm_objects.table.table_constructor import TableMeta

from .query import IQuery
from orm.dissambler import TreeInstruction, TupleInstruction


class SelectQuery[T: Table, *Ts](IQuery):
    def __init__(
        self,
        *tables: tuple[T, *Ts],
        select_list: Optional[Callable[[T, *Ts], None]] = lambda: None,
    ) -> None:
        self._first_table: T = tables[0]
        self._tables: tuple[T, *Ts] = tables

        self._transform_lambda_variables: dict[str, Table] = {}
        self._select_list: Iterable[tuple[str,str]] = self._make_column_list(select_list)

    def _make_column_list(self, select_list: Optional[Callable[[T], None]]) -> Iterable[tuple[str,str]]:
        def _get_parents(tbl_obj: Table, tuple_inst: TupleInstruction) -> None:
            """
            Recursive function tu replace variable names by Select Query
            """
            last_el = tuple_inst.nested_element.name
            parents = tuple_inst.nested_element.parents

            if issubclass(tbl_obj.__class__, Table | TableMeta) and len(parents) == 1:
                # if parents length is 1 says that the element is the table itself
                return res.append((tbl_obj.__table_name__, "*"))

            first_el = tuple_inst.nested_element.parents[1]
            try:
                new_obj = getattr(tbl_obj.__class__, first_el)
            except Exception:
                new_obj = getattr(tbl_obj, first_el, None)

            if last_el not in tbl_obj.__dict__ or not isinstance(new_obj, property):
                if isinstance(new_obj, property):
                    return res.append((tbl_obj.__table_name__, last_el))

                new_ti = TupleInstruction(first_el, NestedElement[str](parents[1:]))
                return _get_parents(new_obj, new_ti)
            return res.append((tbl_obj.__table_name__, last_el))

        instruction_list: list[TupleInstruction] = TreeInstruction(dis.Bytecode(select_list), list).to_list()
        res = []

        lambda_vars = tuple(inspect.signature(select_list).parameters)

        self._update_transform_lambda_variables(lambda_vars)

        for ti in instruction_list:
            obj = self._transform_lambda_variables[ti.var]

            var = obj.__table_name__
            new_nested = ti.nested_element.parents
            new_nested[0] = var
            ti = TupleInstruction(var, NestedElement(new_nested))
            _get_parents(obj, ti)
        return res

    def _update_transform_lambda_variables(self, lambda_vars: tuple[str, ...]):
        for i in range(len(lambda_vars)):
            self._transform_lambda_variables[lambda_vars[i]] = self._tables[i]

    def _convert_select_list(self) -> str:
        if not self._select_list:
            return "*"
        else:
            return ", ".join(".".join(x) for x in self._select_list)

    @property
    def query(self) -> str:
        select_str = self._convert_select_list()
        query = f"SELECT {select_str} FROM {self._first_table.__table_name__}"
        return query
