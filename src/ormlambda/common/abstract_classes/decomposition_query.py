from __future__ import annotations
from collections import defaultdict, deque
import typing as tp
import abc
from ormlambda import Table, Column

from ormlambda.utils.lambda_disassembler.tree_instruction import TupleInstruction, NestedElement
from ormlambda.common.interfaces import IAggregate, IDecompositionQuery, ICustomAlias
from ormlambda import JoinType
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, AggregateFunctionBase
from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.utils.foreign_key import ForeignKey

from ormlambda.types import AliasType, TableType, ColumnType

type TableTupleType[T, *Ts] = tuple[T:TableType, *Ts]
type ValueType = tp.Union[
    property,
    IAggregate,
    Table,
    str,
    ICustomAlias,
]


class DecompositionQueryBase[T: Table, *Ts](IDecompositionQuery[T, *Ts]):
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, by: JoinType = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, by: JoinType = ..., replace_asterisk_char: bool = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, by: JoinType = ..., replace_asterisk_char: bool = ..., joins: tp.Optional[list[IJoinSelector]] = ...) -> None: ...

    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple[*Ts]], *, alias_name: tp.Optional[str] = None, by: JoinType = JoinType.INNER_JOIN, replace_asterisk_char: bool = True, joins: tp.Optional[list[IJoinSelector]] = None, context: tp.Optional[ClauseInfoContext] = None) -> None:
        self._tables: TableTupleType = tables if isinstance(tables, tp.Iterable) else (tables,)

        self._query_list: tp.Callable[[T], tuple] = lambda_query
        self._by: JoinType = by
        self._joins: set[IJoinSelector] = set(joins) if joins is not None else set()
        self._clauses_group_by_tables: dict[TableType, list[ClauseInfo[T]]] = defaultdict(list)
        self._all_clauses: list[ClauseInfo] = []
        self._alias_cache: dict[str, AliasType] = {}
        self._replace_asterisk_char: bool = replace_asterisk_char
        self._context: ClauseInfoContext = context if context else ClauseInfoContext()

        self.__clauses_list_generetor(lambda_query)

    def __getitem__(self, key: str) -> ClauseInfo:
        for clause in self._all_clauses:
            if clause.alias_clause == key:
                return clause

    def __clauses_list_generetor(self, function: tuple | tp.Callable[[T], tp.Any]) -> None:
        if callable(function) and not isinstance(function,type):
            resolved_function = function(self.table)
        else:
            resolved_function = function
        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (resolved_function,)

        for data in resolved_function:
            values: ClauseInfo | list[ClauseInfo] = self.__identify_value_type(data)
            self.__add_clause(values)

        return None

    def __identify_value_type[TProp](self, data: TProp) -> ClauseInfo[T]:
        """
        A method that behaves based on the variable's type
        """

        def validation(data: TProp, type_: ValueType):
            is_table: bool = isinstance(data, type) and issubclass(data, type_)
            return any(
                [
                    isinstance(data, type_),
                    is_table,
                ]
            )

        value_type_mapped: dict[tp.Type[ValueType], tp.Callable[[TProp, TupleInstruction], ClauseInfo[T]]] = {
            ForeignKey: self._fk_type,
            Column: self._column_type,
            IAggregate: self._IAggregate_type,
            Table: self._table_type,
        }

        function = next((handler for cls, handler in value_type_mapped.items() if validation(data, cls)), None)

        if not function:
            raise NotImplementedError(f"type of value '{data}' is not implemented.")

        return function(data)

    def _fk_type[TTable: TableType](self, fk: ForeignKey[T, TTable]) -> list[ClauseInfo[TTable]]:
        # FIXME [x]: How to deal with the foreign table
        self._add_fk_relationship(fk)

        return self._table_type(fk.tright)

    def _column_type[TProp](self, column: ColumnType, alias_table: AliasType[ColumnType[TProp]] = "{table}") -> ClauseInfo[T]:
        # COMMENT: if the property belongs to the main class, the columnn name in not prefixed. This only done if the property comes from any join.

        clause_info = ClauseInfo[T](table=column.table, column=column, alias_table=alias_table, alias_clause="{table}_{column}", context=self._context)
        self._alias_cache[clause_info.alias_clause] = clause_info
        return clause_info

    def _IAggregate_type(self, aggregate_method: AggregateFunctionBase) -> ClauseInfo[T]:
        return aggregate_method

    def _table_type[TType: Table](self, table: TableType[TType]) -> list[ClauseInfo[TableType[TType]]]:
        """
        if the data is Table, means that we want to retrieve all columns
        """
        return self._extract_all_clauses(table)

    def _extract_all_clauses(self, table: TableType[T]) -> list[ClauseInfo[TableType[T]]]:
        # all columns
        return [self._column_type(prop) for prop in table.get_columns()]

    def _search_correct_table_for_prop[TTable: Table](self, table: TableType[TTable], tuple_instruction: TupleInstruction, prop: property) -> ClauseInfo[TTable]:
        temp_table: TableType[TTable] = table

        _, *table_list = tuple_instruction.nested_element.parents
        queue_parent = deque(table_list, maxlen=len(table_list))

        while prop not in temp_table.__properties_mapped__:
            first_property: property = queue_parent.popleft()

            foreign_key: ForeignKey = getattr(temp_table(), first_property)
            foreign_key.orig_object = temp_table

            if not isinstance(foreign_key, ForeignKey):
                raise ValueError(f"'new_table' var must be '{ForeignKey.__name__}' type and is '{type(foreign_key)}'")

            new_table: TTable = foreign_key._referenced_table
            self._alias_cache[first_property] = new_table

            new_ti = TupleInstruction(first_property, NestedElement(table_list))

            new_clause_info = self.return_property_type_from_foreign_key(foreign_key, new_ti, prop)
            if new_clause_info:
                return new_clause_info

            temp_table = new_table

        raise ValueError(f"property '{prop}' does not exist in any inherit tables.")

    def return_property_type_from_foreign_key(self, foreign_key: ForeignKey[TableType, TableType], tuple_instruction: TupleInstruction, prop: property) -> tp.Optional[ClauseInfo]:
        """
        Despite of return 'ClauseInfo' class from the given property, we added the necessary relationship by adding foreign_key into self._joins
        """
        new = foreign_key._referenced_table
        old = foreign_key.orig_object

        if prop in new.__properties_mapped__:
            for ref_table in ForeignKey.MAPPED[old.__table_name__].referenced_tables[new.__table_name__]:
                if ref_table.foreign_key_column == foreign_key.decomposite_fk().cond_1.name:
                    ref_table.orig_table = old

                    self._add_fk_relationship(referenced_table=ref_table)
                    return self._column_type(prop, tuple_instruction)
        return None

    def __add_clause[TTable: TableType](self, clause: list[ClauseInfo[TTable]] | ClauseInfo[TTable]) -> None:
        if isinstance(clause, tp.Iterable):
            [self.__add_clause(x) for x in clause]
            return None

        self._all_clauses.append(clause)
        self._clauses_group_by_tables[clause.table].append(clause)
        return None

    @property
    def table(self) -> T:
        return self.tables[0] if isinstance(self.tables, tp.Iterable) else self.tables

    @property
    def tables(self) -> T:
        return self._tables

    @property
    def lambda_query[*Ts](self) -> tp.Callable[[T], tuple[*Ts]]:
        return self._query_list

    @property
    def all_clauses(self) -> list[ClauseInfo[T]]:
        return self._all_clauses

    @property
    def clauses_group_by_tables(self) -> dict[TableType, list[ClauseInfo[T]]]:
        return self._clauses_group_by_tables

    @property
    def has_foreign_keys(self) -> bool:
        return len(self._joins) > 0

    @property
    def fk_relationship(self) -> set[tuple[TableType, TableType]]:
        return self._joins

    @property
    @abc.abstractmethod
    def query(self) -> str: ...

    @abc.abstractmethod
    def stringify_foreign_key(self, sep: str = "\n") -> str: ...

    @abc.abstractmethod
    def _add_fk_relationship[RTable: Table](self, comparer: ForeignKey[T, RTable]) -> None: ...
