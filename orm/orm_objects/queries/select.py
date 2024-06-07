from queue import Queue
from typing import Callable, Optional, Iterable
import dis

import inspect
from orm.dissambler import TreeInstruction, TupleInstruction, NestedElement
from orm.orm_objects import Table
from orm.orm_objects.table.table_constructor import TableMeta

from .query import IQuery


class TableColumn:
    def __init__(self, table: Table, col: str) -> None:
        self._table: Table = table
        self._column: str = col

    def __repr__(self) -> str:
        return f"{TableColumn.__name__}: T={self._table.__table_name__} col={self._column}"

    @property
    def real_column(self) -> str:
        return self._column

    @property
    def column(self) -> str:
        return f"{self._table.__table_name__}.{self._column} as `{self.alias}`"

    @property
    def alias(self) -> str:
        return f"{self._table.__table_name__}_{self._column}"
    
    def get_all_alias(self)->list[str]:
        return [class_.alias for class_ in self.all_columns(self._table)]


    @classmethod
    def all_columns(cls, table: Table) -> list["TableColumn"]:
        return [cls(table, col) for col in table.__annotations__]


class SelectQuery[T: Table, *Ts](IQuery):
    SELECT = "SELECT"

    def __init__(
        self,
        *tables: tuple[T, *Ts],
        select_lambda: Optional[Callable[[T, *Ts], None]] = lambda: None,
    ) -> None:
        self._first_table: T = tables[0]
        self._tables: tuple[T, *Ts] = tables
        self._tables_heritage: Queue[Table] = Queue()

        self._select_lambda: Optional[Callable[[T, *Ts], None]] = select_lambda
        self._select_list: Iterable[TableColumn] = self._rename_recursive_column_list(select_lambda)

    def _add_el_if_not_in_queue(self, table: Table) -> None:
        if table not in self._tables_heritage.queue:
            self._tables_heritage.put_nowait(table)
            self._tables_heritage.task_done()
        return None

    def _rename_recursive_column_list(self, select_list: Optional[Callable[[T], None]]) -> Iterable[TableColumn]:
        """
        Recursive function tu replace variable names by Select Query

        lambda a: (a.pk_address, a.city.pk_city, a.city.country.pk_country)

        >>> # convert lambda expression into list of values
        >>> select_list = [
        >>>     "a.pk_address",
        >>>     "a.city",
        >>>     "a.city.pk_city",
        >>>     "a.city.country",
        >>>     "a.city.country.pk_country",
        >>> ]
        >>> result = _rename_recursive_column_list(select_list)
        >>> print(result)
        >>> # result = [
        >>> #   "address.pk_address"
        >>> #   "city.*"
        >>> #   "city.pk_city"
        >>> #   "country.*"
        >>> #   "country.pk_country"
        ]
        """

        def _get_parents(tbl_obj: Table, tuple_inst: TupleInstruction) -> None:
            self._add_el_if_not_in_queue(tbl_obj)

            last_el: str = tuple_inst.nested_element.name
            parents: list[str] = tuple_inst.nested_element.parents

            if issubclass(tbl_obj.__class__, Table | TableMeta) and len(parents) == 1:
                # if parents length is 1 says that the element is the table itself
                res.extend(TableColumn.all_columns(tbl_obj))
                return None

            first_el = tuple_inst.nested_element.parents[1]
            try:
                new_obj = getattr(tbl_obj.__class__, first_el)
            except Exception:
                new_obj = getattr(tbl_obj, first_el, None)

            if last_el not in tbl_obj.__dict__ or not isinstance(new_obj, property):
                if isinstance(new_obj, property):
                    return res.append(TableColumn(tbl_obj, last_el))

                new_ti = TupleInstruction(first_el, NestedElement[str](parents[1:]))  # create new TupleInstruction from the second parent to the top
                return _get_parents(new_obj, new_ti)
            return res.append(TableColumn(tbl_obj, last_el))

        # ================== start =========================
        instruction_list: list[TupleInstruction] = TreeInstruction(dis.Bytecode(select_list), list).to_list()
        res: list[TableColumn] = []

        lambda_vars = tuple(inspect.signature(select_list).parameters)

        transform_lambda_variables: dict[str, Table] = self._update_transform_lambda_variables(lambda_vars)

        for ti in instruction_list:
            obj = transform_lambda_variables[ti.var]

            var = obj.__table_name__
            new_nested = ti.nested_element.parents
            new_nested[0] = var
            ti = TupleInstruction(var, NestedElement(new_nested))
            _get_parents(obj, ti)
        return res

    def _update_transform_lambda_variables(self, lambda_vars: tuple[str, ...]):
        dicc: dict[str, Table] = {}
        for i in range(len(lambda_vars)):
            dicc[lambda_vars[i]] = self._tables[i]
        return dicc

    def _convert_select_list(self) -> str:
        if not self._select_list:
            return "*"
        else:
            return ", ".join([col.column for col in self._select_list])

    @property
    def query(self) -> str:
        select_str = self._convert_select_list()
        query = f"{self.SELECT} {select_str} FROM {self._first_table.__table_name__}"
        return query

    def get_involved_tables(self) -> Queue[Table]:
        res_queue: Queue[Table] = Queue(maxsize=self._tables_heritage.qsize())

        for x in self._tables_heritage.queue:
            res_queue.put_nowait(x)
            res_queue.task_done()

        return res_queue
