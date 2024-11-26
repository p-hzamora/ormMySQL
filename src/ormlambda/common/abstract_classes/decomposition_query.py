from __future__ import annotations
from collections import deque
import typing as tp
import inspect
import abc
from ormlambda import Table, Column

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction, TupleInstruction, NestedElement
from ormlambda.common.interfaces import IAggregate, IDecompositionQuery, ICustomAlias
from ormlambda import JoinType
from ormlambda.common.interfaces.IJoinSelector import IJoinSelector
from ormlambda.common.abstract_classes.clause_info import ClauseInfo, AliasType, TableType, ColumnType, ASTERISK
from ormlambda.utils.foreign_key import ForeignKey
from ..errors import UnmatchedLambdaParameterError

if tp.TYPE_CHECKING:
    from ormlambda.utils.foreign_key import ReferencedTable

type TableTupleType[T, *Ts] = tuple[T:TableType, *Ts]
type ValueType = tp.Union[
    property,
    IAggregate,
    Table,
    str,
    ICustomAlias,
]


class DecompositionQueryBase[T: TableType, *Ts](IDecompositionQuery[T, *Ts]):
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple]) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ..., replace_asterisk_char: bool = ...) -> None: ...
    @tp.overload
    def __init__(self, tables: TableTupleType, lambda_query: tp.Callable[[T], tuple], *, alias: bool = ..., alias_name: tp.Optional[str] = ..., by: JoinType = ..., replace_asterisk_char: bool = ..., joins: tp.Optional[list[IJoinSelector]] = ...) -> None: ...

    def __init__(
        self,
        tables: TableTupleType,
        lambda_query: tp.Callable[[T], tuple[*Ts]],
        *,
        alias: bool = True,
        alias_name: tp.Optional[str] = None,
        by: JoinType = JoinType.INNER_JOIN,
        replace_asterisk_char: bool = True,
        joins: tp.Optional[list[IJoinSelector]] = None,
    ) -> None:
        self._tables: TableTupleType = tables if isinstance(tables, tp.Iterable) else (tables,)

        self._lambda_query: tp.Callable[[T], tuple] = lambda_query
        self._alias: bool = alias
        self._alias_name: tp.Optional[str] = alias_name
        self._by: JoinType = by
        self._joins: set[IJoinSelector] = set(joins) if joins is not None else set()

        self._all_clauses: list[ClauseInfo] = []
        self._alias_cache: dict[str, AliasType] = {}
        self._replace_asterisk_char: bool = replace_asterisk_char
        # self.__assign_lambda_variables_to_table(lambda_query)

        self.__clauses_list_generetor(lambda_query)

    def __getitem__(self, key: str) -> ClauseInfo:
        for clause in self._all_clauses:
            if clause.alias == key:
                return clause

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

        if len(lambda_vars) != (expected := len(self._tables)):
            raise UnmatchedLambdaParameterError(expected, found_param=lambda_vars)

        # COMMENT: We don't pass a lambda method because lambda reads the las value of 'i'
        for i, param in enumerate(lambda_vars):
            self._alias_cache[param] = self._tables[i]
        return None

    def __clauses_list_generetor(self, function: tp.Callable[[T], tp.Any]) -> None:
        resolved_function = function
        # Python treats string objects as iterable, so we need to prevent this behavior
        if isinstance(resolved_function, str) or not isinstance(resolved_function, tp.Iterable):
            resolved_function = (resolved_function,)

        for col_index, data in enumerate(resolved_function):
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
        # self.__add_necessary_fk(fk)
        return self._table_type(fk.resolved_function())

    def _column_type[TProp](self, column: ColumnType, alias_table: AliasType[ColumnType[TProp]] = "{table}") -> ClauseInfo[T]:
        # COMMENT: if the property belongs to the main class, the columnn name in not prefixed. This only done if the property comes from any join.

        clause_info = ClauseInfo[T](
            table=column.table,
            column=column,
            alias_table=alias_table,
            alias_clause="{table}_{column}",
        )
        self._alias_cache[clause_info.alias_clause] = clause_info
        return clause_info

    def _IAggregate_type(self, aggregate_method: IAggregate, _: TupleInstruction) -> ClauseInfo[T]:
        return ClauseInfo[T](self.table, aggregate_method)

    def _table_type[TType: TableType](self, table: TType) -> list[ClauseInfo[TType]]:
        """
        if the data is Table, means that we want to retrieve all columns
        """
        return self._extract_all_clauses(table)

    def _extract_all_clauses(self, table: TableType) -> list[ClauseInfo[TableType]]:
        # all columns
        return [self._column_type(prop) for prop in table.get_columns()]

    def _search_correct_table_for_prop[TTable: TableType](self, table: TableType, tuple_instruction: TupleInstruction, prop: property) -> ClauseInfo[TTable]:
        temp_table: TableType = table

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

        return self._all_clauses.append(clause)

    def __add_necessary_fk(self, tables: TableType) -> None:
        old_table = self.table

        table_inherit_list: list[Table] = []
        counter: int = 0
        while tables not in old_table.__dict__.values():
            new_table: TableType = getattr(old_table(), table_inherit_list[counter])

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
    def _add_fk_relationship[T1: TableType, T2: TableType](self, t1: T1, t2: T2, referenced_table: ReferencedTable[T1, T2]) -> None: ...
