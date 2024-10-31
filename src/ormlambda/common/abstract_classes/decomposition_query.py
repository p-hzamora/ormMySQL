from __future__ import annotations
from collections import defaultdict
import typing as tp
import inspect
import abc
from ormlambda import Table

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction, TupleInstruction, NestedElement
from ormlambda.common.interfaces import IAggregate, IDecompositionQuery
from ormlambda import JoinType, ForeignKey
from ormlambda.databases.my_sql.clauses.joins import JoinSelector

from ..errors import DifferentTablesAndVariablesError

type ClauseDataType = property | str
type AliasType[T] = tp.Type[Table] | tp.Callable[[tp.Type[Table]], T]


class ClauseInfo[T: tp.Type[Table]]:
    @tp.overload
    def __init__(self, table: T, column: property, alias_children_resolver: tp.Callable[..., str]): ...
    @tp.overload
    def __init__(self, table: T, column: str, alias_children_resolver: tp.Callable[..., str]): ...

    def __init__(self, table: T, column: ClauseDataType, alias_children_resolver: tp.Callable[[DecompositionQueryBase[T], str], str]):
        self._table: T = table
        self._row_column: ClauseDataType = column
        self._column: str = self._resolve_column(column)
        self._alias_children_resolver: tp.Callable[[DecompositionQueryBase[T], str], str] = alias_children_resolver
        self._alias: tp.Optional[str] = self._alias_children_resolver(self)

        self._query: str = self.__create_value_string(self._column)

    def __repr__(self) -> str:
        return f"{ClauseInfo.__name__}: {self.query}"

    @property
    def column(self) -> ClauseDataType:
        return self._column

    @property
    def alias(self) -> str:
        return self._alias

    @property
    def query(self) -> str:
        return self._query

    @property
    def dtype[TProp](self) -> tp.Optional[tp.Type[TProp]]:
        try:
            return self._table.get_column(self.column).dtype
        except ValueError:
            return None

    def _resolve_column(self, data: ClauseDataType) -> str:
        if isinstance(data, property):
            return self._table.__properties_mapped__[data]

        elif isinstance(data, IAggregate):
            return data.alias_name

        elif isinstance(data, str):
            # TODOL: refactor to base the condition in dict with '*' as key. '*' must to work as special character
            return f"'{data}'" if data != DecompositionQueryBase.CHAR else data

    def __create_value_string(self, name: str) -> str:
        if isinstance(self._row_column, property):
            return self.concat_with_alias(f"{self._table.__table_name__}.{name}")

        if isinstance(self._row_column, IAggregate):
            return self.concat_with_alias(self._row_column.query)

        return self.concat_with_alias(self.column)

    def concat_with_alias(self, column_name: str) -> str:
        alias: None | str = self._alias_children_resolver(self)

        if not alias:
            return column_name
        return f"{column_name} as `{alias}`"


class DecompositionQueryBase[T: tp.Type[Table], *Ts](IDecompositionQuery[T, *Ts]):
    CHAR: str = "*"

    @staticmethod
    def _asterik_resolver(table: tp.Type[Table]):
        return table

    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ..., replace_asterisk_char: bool = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: T, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ..., replace_asterisk_char: bool = ..., joins: tp.Optional[list[JoinSelector]] = ...) -> None: ...

    def __init__(
        self,
        tables: tuple[T, *Ts],
        lambda_query: tp.Callable[[T], tuple[*Ts]],
        *,
        alias: bool = True,
        alias_name: tp.Optional[str] = None,
        by: JoinType = JoinType.INNER_JOIN,
        replace_asterisk_char: bool = True,
        joins: tp.Optional[list[JoinType]] = None,
    ) -> None:
        self._tables: tuple[T, *Ts] = tables if isinstance(tables, tp.Iterable) else (tables,)
        self._lambda_query: tp.Callable[[T], tuple] = lambda_query
        self._alias: bool = alias
        self._alias_name: tp.Optional[str] = alias_name
        self._by: JoinType = by
        self._joins: set[JoinSelector] = set(joins) if joins is not None else set()

        self._clauses_group_by_tables: dict[tp.Type[Table], list[ClauseInfo[T]]] = defaultdict(list)
        self._all_clauses: list[ClauseInfo] = []
        self.alias_cache: dict[str, AliasType] = {self.CHAR: self._asterik_resolver}
        self._replace_asterisk_char: bool = replace_asterisk_char
        self.__assign_lambda_variables_to_table(lambda_query)

        self.__clauses_list_generetor(lambda_query)

    def __getitem__(self, key: str) -> ClauseInfo:
        for clause in self._all_clauses:
            if clause.alias == key:
                return clause

    def alias_children_resolver[Tclause: tp.Type[Table]](self, clause_info: ClauseInfo[Tclause]):
        DEFAULT_ALIAS: str = f"{clause_info._table.__table_name__}_{clause_info._column}"

        if isinstance(clause_info._row_column, IAggregate):
            return clause_info._row_column.alias_name
        return DEFAULT_ALIAS

    def __assign_lambda_variables_to_table(self, _lambda: tp.Callable[[T], None]) -> None:
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

        # COMMENT: We don't pass a lambda method because lambda reads the las value of 'i'
        for i, param in enumerate(lambda_vars):
            self.alias_cache[param] = self._tables[i]
        return None

    def __clauses_list_generetor(self, function: tp.Callable[[T], tp.Any]) -> None:
        if not callable(function):
            return None
        try:
            resolved_function = function(*self._tables)
        except TypeError:
            raise DifferentTablesAndVariablesError

        tree_list = TreeInstruction(function).to_list()
        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (resolved_function,)

        for col_index, last_data in enumerate(resolved_function):
            ti = tree_list[col_index] if tree_list else TupleInstruction(self.CHAR, NestedElement(self.CHAR))

            values: ClauseInfo | list[ClauseInfo] = self.__identify_value_type(last_data, ti)

            if isinstance(values, tp.Iterable):
                [self.__add_clause(x) for x in values]
            else:
                self.__add_clause(values)

        return None

    def __identify_value_type[TProp](self, last_data: TProp, tuple_instruction: TupleInstruction) -> ClauseInfo[T]:
        """
        A method that behaves based on the variable's type
        """

        if isinstance(last_data, property):
            if tuple_instruction.var == self.CHAR:
                table_left = self.table
            else:
                table_left = self.alias_cache[tuple_instruction.var]

            if last_data in table_left.__properties_mapped__:
                # if self.table != table_left:
                #     self._add_fk_relationship(self.table, table_left)
                return ClauseInfo[T](table_left, last_data, self.alias_children_resolver)

            for table in self.tables:
                try:
                    return self._search_correct_table_for_prop(table, tuple_instruction, last_data)
                except ValueError:
                    continue

        elif isinstance(last_data, IAggregate):
            return ClauseInfo[T](self.table, last_data, self.alias_children_resolver)

        # if value is a Table instance (when you need to retrieve all columns) we'll ensure that all JOINs are added
        elif isinstance(last_data, type) and issubclass(last_data, Table):
            if last_data not in self._tables:
                self.__add_necessary_fk(tuple_instruction, last_data)
            # all columns
            clauses: list[ClauseInfo] = []
            for prop in last_data.__properties_mapped__:
                if isinstance(prop, property):
                    clauses.append(self.__identify_value_type(prop, tuple_instruction))
            return clauses

        elif isinstance(last_data, str):
            # COMMENT: use self.table instead self._tables because if we hit this conditional, means that
            # COMMENT: alias_cache to replace '*' by all columns
            if self._replace_asterisk_char and (replace_value := self.alias_cache.get(last_data, None)) is not None:
                return self.__identify_value_type(replace_value(self.table), tuple_instruction)
            return ClauseInfo[T](self.table, last_data, alias_children_resolver=self.alias_children_resolver)

        raise NotImplementedError(f"type of value '{last_data}' is not implemented.")

    def _search_correct_table_for_prop[TTable](self, table: tp.Type[Table], tuple_instruction: TupleInstruction, prop: property) -> ClauseInfo[TTable]:
        temp_table: tp.Type[Table] = table

        _, *table_list = tuple_instruction.nested_element.parents
        counter: int = 0
        while prop not in temp_table.__properties_mapped__:
            new_table: TTable = getattr(temp_table(), table_list[counter])

            if not isinstance(new_table, type) or not issubclass(new_table, Table):
                raise ValueError(f"new_table var must be '{Table.__class__}' type and is '{type(new_table)}'")
            self._add_fk_relationship(temp_table, new_table)

            temp_table = new_table
            counter += 1

            if prop in new_table.__properties_mapped__:
                return ClauseInfo[TTable](new_table, prop, self.alias_children_resolver)

        raise ValueError(f"property '{prop}' does not exist in any inherit tables.")

    def __add_clause[Tc: tp.Type[Table]](self, clause: ClauseInfo[Tc]) -> None:
        self._all_clauses.append(clause)
        self._clauses_group_by_tables[clause._table].append(clause)
        return None

    def __add_necessary_fk(self, tuple_instruction: TupleInstruction, tables: tp.Type[Table]) -> None:
        old_table = self.table

        table_inherit_list: list[Table] = tuple_instruction.nested_element.parents[1:]
        counter: int = 0
        while tables not in old_table.__dict__.values():
            new_table: tp.Type[Table] = getattr(old_table(), table_inherit_list[counter])

            if not issubclass(new_table, Table):
                raise ValueError(f"new_table var must be '{Table.__class__}' type and is '{type(new_table)}'")

            self._add_fk_relationship(old_table, new_table)

            if tables in new_table.__dict__.values():
                return self._add_fk_relationship(new_table, tables)

            old_table = new_table
            counter += 1

        return self._add_fk_relationship(old_table, tables)

    @property
    def table(self) -> T:
        return self.tables[0] if isinstance(self.tables, tp.Iterable) else self.tables

    @property
    def tables(self) -> T:
        return self._tables

    @property
    def lambda_query[*Ts](self) -> tp.Callable[[T], tuple[*Ts]]:
        return self._lambda_query

    @property
    def all_clauses(self) -> list[ClauseInfo[T]]:
        return self._all_clauses

    @property
    def clauses_group_by_tables(self) -> dict[tp.Type[Table], list[ClauseInfo[T]]]:
        return self._clauses_group_by_tables

    @property
    def has_foreign_keys(self) -> bool:
        return len(self._joins) > 0

    @property
    def fk_relationship(self) -> set[tuple[tp.Type[Table], tp.Type[Table]]]:
        return self._joins

    @property
    @abc.abstractmethod
    def query(self) -> str: ...

    @property
    def alias(self) -> str:
        return self._alias

    @property
    def alias_name(self) -> str:
        return self._alias_name

    @alias_name.setter
    def alias_name(self, value: tp.Optional[str]) -> None:
        if value is None and self._alias:
            self._alias = False
        else:
            self._alias = True

        self._alias_name = value

    def stringify_foreign_key(self, sep: str = "\n") -> str:
        sorted_joins = JoinSelector.sort_join_selectors(self._joins)
        return f"{sep}".join([join.query for join in sorted_joins])

    def _add_fk_relationship[T1: tp.Type[Table], T2: tp.Type[Table]](self, t1: T1, t2: T2) -> None:
        lambda_relationship = ForeignKey.MAPPED[t1.__table_name__].referenced_tables[t2.__table_name__].relationship

        tables = list(self._tables)
        if t2 not in tables:
            tables.append(t2)
        self._tables = tuple(tables)
        return self._joins.add(JoinSelector[T1, T2](t1, t2, self._by, where=lambda_relationship))
