from __future__ import annotations
from collections import defaultdict
import typing as tp
import inspect
import abc
from ormlambda import Table

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction
from ormlambda.common.interfaces import IAggregate, IDecompositionQuery
from ormlambda import JoinType, ForeignKey
from ormlambda.databases.my_sql.clauses.joins import JoinSelector
from ormlambda.utils.module_tree.dfs_traversal import DFSTraversal

ClauseDataType = tp.TypeVar("ClauseDataType", bound=tp.Union[property, str])


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
        pass

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

    def _resolve_column(self, data: ClauseDataType) -> str:
        if isinstance(data, property):
            return self._table.__properties_mapped__[data]

        elif isinstance(data, IAggregate):
            return data.alias_name

        elif isinstance(data, str):
            # TODOL: refactor to base the condition in dict with '*' as key. '*' must to work as special character
            return f"'{data}'" if data != "*" else data

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


class DecompositionQueryBase[T: tp.Type[Table]](IDecompositionQuery[T]):
    def __init__[*Ts](
        self,
        table: T,
        lambda_query: tp.Callable[[T], tuple[*Ts]],
        *,
        alias: bool = True,
        alias_name: tp.Optional[str] = None,
        by: JoinType = JoinType.INNER_JOIN,
        replace_asterisk_char: bool = True,
    ) -> None:
        self._table: T = table
        self._lambda_query: tp.Callable[[T], tuple[Ts]] = lambda_query
        self._alias: bool = alias
        self._alias_name: tp.Optional[str] = alias_name
        self._by: JoinType = by

        self._fk_relationship: set[tuple[tp.Type[Table], tp.Type[Table]]] = set()
        self._clauses_group_by_tables: dict[tp.Type[Table], list[ClauseInfo[T]]] = defaultdict(list)
        self._all_clauses: list[ClauseInfo] = []
        self.alias_cache: dict[str, tp.Any] = {"*": lambda x: x}
        self._replace_asterisk_char: bool = replace_asterisk_char
        self.__assign_lambda_variables_to_table(lambda_query)

        self.__clauses_list_generetor(lambda_query)

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

        for param in lambda_vars:
            self.alias_cache[param] = lambda x: self._table
        return None

    def __clauses_list_generetor(self, function: tp.Callable[[T], tp.Any]) -> None:
        if not callable(function):
            return None

        resolved_function = function(self._table)

        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (resolved_function,)

        for index, value in enumerate(resolved_function):
            values: ClauseInfo | list[ClauseInfo] = self._identify_value_type(index, value, function)

            if isinstance(values, tp.Iterable):
                [self.add_clause(x) for x in values]
            else:
                self.add_clause(values)

        return None

    def _identify_value_type[TProp](self, index: int, value: TProp, function) -> ClauseInfo[T]:
        """
        A method that behaves based on the variable's type
        """
        if isinstance(value, property):
            if value in self._table.__properties_mapped__:
                return ClauseInfo[T](self._table, value, self.alias_children_resolver)

            return self._search_correct_table_for_prop(index, function, value)

        elif isinstance(value, IAggregate):
            return ClauseInfo[T](self._table, value, self.alias_children_resolver)

        # if value is a Table instance (when you need to retrieve all columns) we'll ensure that all INNER JOINs are added
        elif isinstance(value, type) and issubclass(value, Table):
            if self._table != value:
                self._add_necessary_fk(index, function, value)
            # all columns
            clauses: list[ClauseInfo] = []
            for prop in value.__properties_mapped__:
                if isinstance(prop, property):
                    clauses.append(self._identify_value_type(index, prop, function))
            return clauses

        elif isinstance(value, str):
            # TODOM: alias_cache to replace '*' by all columns
            if self._replace_asterisk_char and (replace_value := self.alias_cache.get(value, None)) is not None:
                return self._identify_value_type(index, replace_value(self._table), function)
            return ClauseInfo[T](self._table, value, alias_children_resolver=self.alias_children_resolver)
        
        elif isinstance(value,bool):
            ...

        raise NotImplementedError(f"type of value '{value}' is not implemented.")

    def _search_correct_table_for_prop[TTable](self, index: int, function: tp.Callable[[T], tp.Any], prop: property) -> ClauseInfo[TTable]:
        tree_list = TreeInstruction(function).to_list()
        temp_table: tp.Type[Table] = self._table

        table_list: list[Table] = tree_list[index].nested_element.parents[1:]
        counter: int = 0
        while prop not in temp_table.__properties_mapped__:
            new_table: TTable = getattr(temp_table(), table_list[counter])

            if not isinstance(new_table, type) or not issubclass(new_table, Table):
                raise ValueError(f"new_table var must be '{Table.__class__}' type and is '{type(new_table)}'")
            self.__add_fk_relationship(temp_table, new_table)

            temp_table = new_table
            counter += 1

            if prop in new_table.__properties_mapped__:
                return ClauseInfo[TTable](new_table, prop, self.alias_children_resolver)

        raise ValueError(f"property '{prop}' does not exist in any inherit table.")

    def add_clause[Tc: tp.Type[Table]](self, clause: ClauseInfo[Tc]) -> None:
        self._all_clauses.append(clause)
        self._clauses_group_by_tables[clause._table].append(clause)

        return None

    def _add_necessary_fk(self, index: int, function: tp.Callable[[T], tp.Any], table: tp.Type[Table]) -> None:
        tree_list = TreeInstruction(function).to_list()
        old_table: tp.Type[Table] = self._table

        table_list: list[Table] = tree_list[index].nested_element.parents[1:]
        counter: int = 0
        while table not in old_table.__dict__.values():
            new_table: tp.Type[Table] = getattr(old_table(), table_list[counter])

            if not issubclass(new_table, Table):
                raise ValueError(f"new_table var must be '{Table.__class__}' type and is '{type(new_table)}'")

            self.__add_fk_relationship(old_table, new_table)

            if table in new_table.__dict__.values():
                self.__add_fk_relationship(new_table, table)
                return None

            old_table = new_table
            counter += 1

        self.__add_fk_relationship(old_table, table)
        return None

    @property
    def table(self) -> T:
        return self._table

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
        return len(self._fk_relationship) > 0

    @property
    def fk_relationship(self) -> set[tuple[tp.Type[Table], tp.Type[Table]]]:
        return self._fk_relationship

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
        graph: dict[tp.Type[Table], list[tp.Type[Table]]] = defaultdict(list)
        for left, right in self.fk_relationship:
            graph[left].append(right)

        dfs = DFSTraversal.sort(graph)[::-1]
        query: list = []
        for l_tbl in dfs:
            list_r_tbl = graph[l_tbl]
            if not list_r_tbl:
                continue

            for r_tbl in list_r_tbl:
                lambda_relationship = ForeignKey.MAPPED[l_tbl.__table_name__].referenced_tables[r_tbl.__table_name__].relationship

                join = JoinSelector(l_tbl, r_tbl, by=self._by, where=lambda_relationship)
                query.append(join.query)

        return f"{sep}".join(query)

    def __add_fk_relationship(self, t1: Table, t2: Table) -> None:
        self._fk_relationship.add((t1, t2))
        return None
