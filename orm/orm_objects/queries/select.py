from typing import Callable, Iterator, Optional, Type, override

import inspect

from ...dissambler import TreeInstruction, TupleInstruction, NestedElement
from ...interfaces.IQuery import IQuery
from ...orm_objects import Table, ForeignKey
from ...orm_objects.table.table_constructor import TableMeta
from ...orm_objects.queries.joins import JoinSelector, JoinType


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

    def get_all_alias(self) -> list[str]:
        return [class_.alias for class_ in self.all_columns(self._table)]

    @classmethod
    def all_columns(cls, table: Table) -> Iterator["TableColumn"]:
        for col in table.__annotations__:
            yield cls(table, col)

    def __hash__(self) -> int:
        return hash((self._table, self._column))

    def __eq__(self, __value: "TableColumn") -> bool:
        if isinstance(__value, TableColumn):
            return self._table.__table_name__ == __value._table.__table_name__ and self._column == __value._column
        return False


class SelectQuery[T: Table, *Ts](IQuery):
    SELECT = "SELECT"

    def __init__(
        self,
        tables: T | tuple[T, *Ts] = (),
        select_lambda: Optional[Callable[[T, *Ts], None]] = lambda: None,
        *,
        by: JoinType = JoinType.INNER_JOIN,
    ) -> None:
        if not isinstance(tables, tuple):
            tables = tuple([tables])

        self._first_table: T = tables[0]
        self._tables: tuple[T, *Ts] = tables
        self._select_lambda: Optional[Callable[[T, *Ts], None]] = select_lambda
        self._by: JoinType = by

        self._tables_heritage: list[tuple[Table, Table]] = []
        self._lambda_var_to_table_dicc: dict[str, Table] = self._assign_lambda_variables_to_table(select_lambda)

        self._select_list: list[TableColumn] = self._rename_recursive_column_list(select_lambda)

    def _rename_recursive_column_list(self, _lambda: Optional[Callable[[T], None]]) -> list[TableColumn]:
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
        instruction_list: list[TupleInstruction] = TreeInstruction(_lambda).to_list()
        column_list: list[TableColumn] = []

        for ti in instruction_list:
            obj = self._lambda_var_to_table_dicc[ti.var]

            var = obj.__table_name__
            new_nested = ti.nested_element.parents
            new_nested[0] = var
            ti = TupleInstruction(var, NestedElement(new_nested))
            self._get_parents(obj, ti, column_list)
        return column_list

    def _get_parents(self, tbl_obj: Table, tuple_inst: TupleInstruction, column_list: list[TableColumn]) -> None:
        if self._user_want_all_col(tbl_obj, tuple_inst):
            column_list.extend(list(TableColumn.all_columns(tbl_obj)))
            return None

        # if the 'last_el' var is a property, we'll know the user will want retrieve a column of the same instance of the 'tbl_obj'. Otherwise the user will want to get a column of the other instance
        last_el: str = tuple_inst.nested_element.name
        if self._user_want_column_of_the_same_table(tbl_obj, tuple_inst):
            return column_list.append(TableColumn(tbl_obj, last_el))

        parents: list[str] = tuple_inst.nested_element.parents
        first_el = parents[1]
        new_ti = TupleInstruction(first_el, NestedElement[str](parents[1:]))  # create new TupleInstruction from the second parent to the top
        new_attr = self.get_attribute_of(tbl_obj, first_el)  # could be Table or property

        self._add_fk_relationship(tbl_obj, new_attr)
        return self._get_parents(new_attr, new_ti, column_list)

    def _add_fk_relationship(self, t1: Table, t2: Table) -> None:
        tuple_ = tuple([t1, t2])
        if tuple_ not in self._tables_heritage:
            self._tables_heritage.append(tuple_)
        return None

    @staticmethod
    def _user_want_all_col(tbl: Table, ti: TupleInstruction) -> bool:
        """
        if  ti.nested_element.parents length is 1 says that the element is the table itself (table.*)
        """
        return issubclass(tbl.__class__, Table | TableMeta) and len(ti.nested_element.parents) == 1

    def _user_want_column_of_the_same_table(self, table: Table, ti: TupleInstruction) -> bool:
        last_el: str = ti.nested_element.name
        first_el = ti.nested_element.parents[1]

        table_attr = self.get_attribute_of(table, first_el)

        return last_el in table.__dict__ and isinstance(table_attr, property)

    @staticmethod
    def get_attribute_of[TProp: Table](table: TProp, _value: str) -> Optional[TProp | property]:
        try:
            return getattr(table.__class__, _value)
        except Exception:
            return getattr(table, _value, None)

    def _assign_lambda_variables_to_table(self, _lambda: Callable[[T], None]) -> dict[str, Type[Table]]:
        """
        return a dictionary with the lambda's parameters as keys and Type[Table] as the values


        >>> res = _assign_lambda_variables_to_table(lambda a,ci,co: ...)
        >>> print(res)
        >>> # {
        >>> #   "a": Address,
        >>> #   "ci": City,
        >>> #   "co": Country,
        >>> # }
        """
        lambda_vars = tuple(inspect.signature(_lambda).parameters)

        dicc: dict[str, Table] = {}
        for i in range(len(lambda_vars)):
            dicc[lambda_vars[i]] = self._tables[i]
        return dicc

    def _convert_select_list(self) -> str:
        self._select_list = self._select_list if self._select_list else tuple(TableColumn.all_columns(self._first_table))

        return ", ".join(col.column for col in self._select_list)

    @override
    @property
    def query(self) -> str:
        select_str = self._convert_select_list()
        query: str = f"{self.SELECT} {select_str} FROM {self._first_table.__table_name__}"

        involved_tables = self.get_involved_tables()
        if not involved_tables:
            return query

        sub_query: str = ""
        for l_tbl, r_tbl in involved_tables:
            join = JoinSelector[l_tbl, r_tbl](l_tbl, r_tbl, by=self._by, where=ForeignKey[l_tbl, r_tbl].MAPPED[l_tbl.__table_name__][r_tbl])
            sub_query += f" {join.query}"

        query += sub_query
        return query

    def get_involved_tables(self) -> tuple[tuple[Table, Table]]:
        return tuple(self._tables_heritage)
