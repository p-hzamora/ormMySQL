from __future__ import annotations
from typing import Any, Callable, Iterable, Optional, Type, overload, TYPE_CHECKING
from abc import abstractmethod


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.types import TupleJoinType, ColumnType
    from ormlambda.sql.types import compileOptions
    from ormlambda.sql.types import AliasType

    from ormlambda.sql.clauses.join import JoinContext
    from ormlambda.common.enums import JoinType

    from ..types import OrderTypes
    from ..types import Tuple
    from ..types import TypeExists
    from ..types import WhereTypes
    from ..types import SelectCols


from ormlambda.sql.elements import Element


class IStatements[T: Table](Element):
    @abstractmethod
    def create_table(self, if_exists: TypeExists = "fail") -> None: ...

    @abstractmethod
    def drop_table(self) -> None: ...

    # #TODOL [ ]: We must to implement this mehtod
    # @abstractmethod
    # def drop_table(self)->None: ...

    @abstractmethod
    def table_exists(self) -> bool: ...

    # region insert
    @overload
    def insert(self, values: T) -> None:
        """
        PARAMS
        ------
        - values: Recieves a single object that must match the model's type
        """
        ...

    @overload
    def insert(self, values: list[T]) -> None:
        """
        PARAMS
        ------
        - values: Recieves a list of the same objects as the model
        """
        ...

    @abstractmethod
    def insert(self, values: T | list[T]) -> None: ...

    # endregion
    # region upsert
    @overload
    def upsert(self, values: T) -> None:
        """
        PARAMS
        ------
        - values: Recieves a single object that must match the model's type
        """
        ...

    @overload
    def upsert(self, values: list[T]) -> None:
        """
        PARAMS
        ------
        - values: Recieves a list of the same objects as the model
        """
        ...

    @abstractmethod
    def upsert(self, values: list[T]) -> None:
        """
        Try to insert new values in the table, if they exist, update them
        """
        ...

    @overload
    def update(self, dicc: list[dict[ColumnType, Any]]) -> None:
        """
        An Iterable of ColumnType

        type ColumnType[TProp]:
            - TProp
            - Column[TProp]
            - tuple[Column]
        """
        ...

    @overload
    def update(self, dicc: dict[ColumnType, Any]) -> None:
        """
        type ColumnType[TProp]:
            - TProp
            - Column[TProp]
            - tuple[Column]
        """
        ...

    @abstractmethod
    def update(self, dicc) -> None: ...

    # endregion
    # region limit
    @abstractmethod
    def limit(self, number: int) -> IStatements[T]: ...

    # endregion
    # region offset
    @abstractmethod
    def offset(self, number: int) -> IStatements[T]: ...

    # endregion
    # region count
    @abstractmethod
    def count[TProp](
        self,
        selection: Optional[SelectCols[T, TProp]] = ...,
        alias: AliasType[T] = ...,
    ) -> Optional[int]: ...

    # endregion
    # region delete
    @overload
    def delete(self) -> None: ...

    @overload
    def delete(self, instance: T) -> None: ...

    @overload
    def delete(self, instance: list[T]) -> None: ...
    @abstractmethod
    def delete(self, instance: Optional[T | list[T]] = ...) -> None: ...

    # endregion

    # region where
    @overload
    def where(self, conditions: WhereTypes[T]) -> IStatements[T]: ...
    @overload
    def where(self, conditions: WhereTypes[T], restrictive: bool) -> IStatements[T]: ...
    @abstractmethod
    def where(self, conditions: WhereTypes[T] = None, restrictive: bool = ...) -> IStatements[T]: ...

    # endregion

    # region having

    @overload
    def having(self, conditions: WhereTypes[T]) -> IStatements[T]: ...
    @overload
    def having(self, conditions: WhereTypes[T], restrictive: bool) -> IStatements[T]: ...

    @abstractmethod
    def having(self, conditions: WhereTypes[T] = None, restrictive: bool = ...) -> IStatements[T]: ...

    # endregion
    # region order
    @overload
    def order[TValue](self, columns: SelectCols[T, TValue]) -> IStatements[T]: ...
    @overload
    def order[TValue](self, columns: SelectCols[T, TValue], order_type: OrderTypes) -> IStatements[T]: ...
    @overload
    def order[TValue](self, columns: Iterable[SelectCols[T, TValue]]) -> IStatements[T]: ...
    @overload
    def order[TValue](self, columns: Iterable[SelectCols[T, TValue]], order_type: Iterable[OrderTypes]) -> IStatements[T]: ...
    @abstractmethod
    def order[TValue](self, columns, order_type=...) -> IStatements[T]: ...

    # endregion

    # region max
    @abstractmethod
    def max[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: AliasType[T] = ...,
    ) -> int: ...
    # endregion
    # region min
    @abstractmethod
    def min[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: AliasType[T] = ...,
    ) -> int: ...
    # endregion
    # region sum
    @abstractmethod
    def sum[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: AliasType[T] = ...,
    ) -> int: ...

    @overload
    def join[FKTable](self, joins: TupleJoinType[FKTable] | tuple[*TupleJoinType[FKTable]]) -> JoinContext[tuple[*TupleJoinType[FKTable]]]: ...

    # endregion
    # region select
    @overload
    def select[T1](self, selector: Callable[[T], T1 | tuple[T1]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> tuple[T1, ...]: ...
    @overload
    def select[*T1](self, selector: Callable[[T], tuple[*T1]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> Tuple[*T1]: ...
    @overload
    def select(self, *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> Tuple[T]: ...

    # region deal with flavours
    @overload
    def select[*TRes](self, selector: Callable[[T], tuple[*TRes]] = ..., *, flavour: Type[tuple], **kwargs) -> tuple[tuple[*TRes]]: ...
    @overload
    def select[TFlavour](self, selector: Callable[[T], tuple] = ..., *, flavour: Type[TFlavour], **kwargs) -> tuple[TFlavour, ...]: ...

    # endregion

    @abstractmethod
    def select(
        self,
        selector=...,
        *,
        flavour=...,
        by=...,
        alias=...,
        avoid_duplicates=...,
    ): ...

    # endregion
    # region select_one
    @overload
    def select_one(self, *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> T: ...
    @overload
    def select_one[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[tuple], avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[list], avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[TFlavour](self, selector: Callable[[T], Any], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[TFlavour], avoid_duplicates: bool = ...) -> TFlavour: ...
    @overload
    def select_one(self, selector: Callable[[T], Any], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[dict], avoid_duplicates: bool = ...) -> dict[str, Any]: ...

    @abstractmethod
    def select_one(
        self,
        selector=...,
        *,
        by=...,
        alias=...,
        flavour=...,
        avoid_duplicates=...,
    ): ...

    # endregion

    # region first
    @overload
    def first(self, *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> T: ...
    @overload
    def first[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def first[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[tuple], avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def first[*TRes](self, selector: Callable[[T], tuple[*TRes]], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[list], avoid_duplicates: bool = ...) -> tuple[*TRes]: ...
    @overload
    def first[TFlavour](self, selector: Callable[[T], Any], *, by: JoinType = ..., alias: Optional[AliasType[ColumnType]] = ..., flavour: Type[TFlavour], avoid_duplicates: bool = ...) -> TFlavour: ...
    @overload
    def first(self, selector: Callable[[T], tuple], *, by: JoinType = ..., flavour: Type[dict], alias: Optional[AliasType[ColumnType]] = ..., avoid_duplicates: bool = ...) -> dict[str, Any]: ...

    @abstractmethod
    def first(
        self,
        selector=...,
        *,
        by=...,
        alias=...,
        flavour=...,
        avoid_duplicates=...,
    ): ...

    # endregion

    # region groupby
    @overload
    def groupby[TRepo](self, column: list[SelectCols[T, TRepo]]) -> IStatements[T]: ...
    @overload
    def groupby[TRepo](self, column: SelectCols[T, TRepo]) -> IStatements[T]: ...
    @abstractmethod
    def groupby[TRepo](self, column: list[SelectCols[T, TRepo]] | SelectCols[T, TRepo]) -> IStatements[T]: ...

    @abstractmethod
    def query(self, component: Optional[compileOptions]) -> str: ...

    # endregion
