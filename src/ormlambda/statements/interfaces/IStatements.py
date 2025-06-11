from __future__ import annotations
from typing import Any, Callable, Optional, Type, overload, TYPE_CHECKING
from enum import Enum
from abc import abstractmethod


if TYPE_CHECKING:
    from ormlambda.repository import BaseRepository
    from ormlambda import Table
    from ormlambda.sql.clause_info import IAggregate
    from ormlambda.sql.types import TupleJoinType, ColumnType
    from ormlambda.sql.clauses.join import JoinContext
    from ormlambda.common.enums import JoinType
    from ormlambda.sql.clause_info import ClauseInfo
    from ormlambda.sql.types import AliasType

from ..types import (
    OrderTypes,
    Tuple,
    Select2,
    Select3,
    Select4,
    Select5,
    Select6,
    Select7,
    Select8,
    Select9,
    Select10,
    TypeExists,
    WhereTypes,
    SelectCols,
)
from ormlambda.sql.elements import Element


class IStatements[T: Table](Element):
    @abstractmethod
    def create_table(self, if_exists: TypeExists = "fail") -> None: ...

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
            - AsteriskType
            - tuple[Column]
        """
        ...

    @overload
    def update(self, dicc: dict[ColumnType, Any]) -> None:
        """
        type ColumnType[TProp]:
            - TProp
            - Column[TProp]
            - AsteriskType
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
        selection: None | SelectCols[T, TProp] = ...,
        alias: str = ...,
        execute: bool = False,
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
    def where[LProp, RTable, RProp](self, conditions: Callable[[T], WhereTypes[T, LProp, RTable, RProp]]) -> IStatements[T]: ...

    @abstractmethod
    def where[LProp, RTable, RProp](self, conditions: WhereTypes[T, LProp, RTable, RProp] = None) -> IStatements[T]: ...

    # endregion

    # region having

    @overload
    def having[LProp, RTable, RProp](self, conditions: Callable[[T], WhereTypes[T, LProp, RTable, RProp]]) -> IStatements[T]: ...

    @abstractmethod
    def having[LProp, RTable, RProp](self, conditions: WhereTypes[T, LProp, RTable, RProp] = None) -> IStatements[T]: ...

    # endregion
    # region order
    @abstractmethod
    def order[TValue](self, columns: SelectCols[T, TValue], order_type: OrderTypes) -> IStatements[T]: ...

    # endregion
    # region concat
    @overload
    def concat(self, selector: SelectCols[T, str], alias: str = "concat") -> IAggregate: ...

    # endregion
    # region max
    @abstractmethod
    def max[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: Optional[str] = ...,
        execute: bool = False,
    ) -> int: ...
    # endregion
    # region min
    @abstractmethod
    def min[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: Optional[str] = ...,
        execute: bool = False,
    ) -> int: ...
    # endregion
    # region sum
    @abstractmethod
    def sum[TProp](
        self,
        column: SelectCols[T, TProp],
        alias: Optional[str] = ...,
        execute: bool = False,
    ) -> int: ...

    @overload
    def join[FKTable](self, joins: TupleJoinType[FKTable] | tuple[*TupleJoinType[FKTable]]) -> JoinContext[tuple[*TupleJoinType[FKTable]]]: ...

    # endregion
    # region select
    type SelectorType[TOri, *T] = Callable[[TOri], tuple[*T]] | tuple[*T]
    type SelectorFlavourType[T, TResponse] = Optional[Callable[[T], TResponse]] | TResponse
    type SelectorOneType[T, TResponse] = Callable[[T, TResponse]] | TResponse

    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](self, selector: SelectorType[T, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], *, by: Optional[Enum] = ...) -> Select10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9](self, selector: SelectorType[T, T1, T2, T3, T4, T5, T6, T7, T8, T9], *, by: Optional[Enum] = ...) -> Select9[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8](self, selector: SelectorType[T, T1, T2, T3, T4, T5, T6, T7, T8], *, by: Optional[Enum] = ...) -> Select8[T1, T2, T3, T4, T5, T6, T7, T8]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7](self, selector: SelectorType[T, T1, T2, T3, T4, T5, T6, T7], *, by: Optional[Enum] = ...) -> Select7[T1, T2, T3, T4, T5, T6, T7]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6](self, selector: SelectorType[T, T1, T2, T3, T4, T5, T6], *, by: Optional[Enum] = ...) -> Select6[T1, T2, T3, T4, T5, T6]: ...
    @overload
    def select[T1, T2, T3, T4, T5](self, selector: SelectorType[T, T1, T2, T3, T4, T5], *, by: Optional[Enum] = ...) -> Select5[T1, T2, T3, T4, T5]: ...
    @overload
    def select[T1, T2, T3, T4](self, selector: SelectorType[T, T1, T2, T3, T4], *, by: Optional[Enum] = ...) -> Select4[T1, T2, T3, T4]: ...
    @overload
    def select[T1, T2, T3](self, selector: SelectorType[T, T1, T2, T3], *, by: Optional[Enum] = ...) -> Select3[T1, T2, T3]: ...
    @overload
    def select[T1, T2](self, selector: SelectorType[T, T1, T2], *, by: Optional[Enum] = ...) -> Select2[T1, T2]: ...
    @overload
    def select[T1](self, selector: SelectorType[T, T1], *, by: Optional[Enum] = ...) -> Tuple[T1]: ...
    @overload
    def select[T1](self, selector: Callable[[T], T1], *, by: Optional[Enum] = ...) -> Tuple[T1]: ...
    @overload
    def select(self) -> Tuple[T]: ...

    # @overload
    # def select[TFlavour](self, selector: Optional[Callable[[T], tuple]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour], by: Optional[Enum] = ..., **kwargs) -> TFlavour: ...
    @overload
    def select[TRes](self, selector: SelectorFlavourType[T, TRes] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> tuple[TRes, ...]: ...
    @overload
    def select[*TRes](self, selector: SelectorFlavourType[T, tuple[*TRes]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> tuple[tuple[*TRes]]: ...
    @overload
    def select[TFlavour](self, selector: SelectorFlavourType[T, tuple] = ..., *, flavour: Type[TFlavour], by: Optional[Enum] = ..., alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> tuple[TFlavour, ...]: ...

    @abstractmethod
    def select[TValue, TFlavour, P](self, selector: SelectorFlavourType[T, tuple[TValue, P]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour] = ..., by: JoinType = ..., alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs): ...

    # endregion
    # region select_one
    @overload
    def select_one(self) -> T: ...
    @overload
    def select_one[TFlavour](self, *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @overload
    def select_one[T1](self, selector: SelectorOneType[T, T1 | tuple[T1]], *, by: Optional[Enum] = ...) -> T1: ...
    @overload
    def select_one[*TRes](self, selector: SelectorOneType[T, tuple[*TRes]], *, by: Optional[Enum] = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[T1](self, selector: SelectorOneType[T, tuple[T1]], *, by: Optional[Enum] = ..., flavour: Type, alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> T1: ...
    @overload
    def select_one[T1, TFlavour](self, selector: SelectorOneType[T, T1], *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @overload
    def select_one[*TRest](self, selector: SelectorOneType[T, tuple[*TRest]], *, by: Optional[Enum] = ..., flavour: Type[tuple], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> tuple[*TRest]: ...
    @overload
    def select_one[TFlavour](self, selector: SelectorOneType[T, tuple], *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @abstractmethod
    def select_one[TValue, TFlavour, *TRest](
        self,
        selector: Optional[SelectorOneType[T, tuple[TValue, *TRest]]] = lambda: None,
        *,
        flavour: Type[TFlavour] = ...,
        by: Optional[Enum] = ...,
    ): ...

    # endregion

    # region first
    @overload
    def first(self) -> T: ...
    @overload
    def first[T1](self, selector: SelectorOneType[T, T1 | tuple[T1]], *, by: Optional[Enum] = ...) -> T1: ...
    @overload
    def first[*TRes](self, selector: SelectorOneType[T, tuple[*TRes]], *, by: Optional[Enum] = ...) -> tuple[*TRes]: ...
    @overload
    def first[TFlavour](self, *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @overload
    def first[T1](self, selector: SelectorOneType[T, tuple[T1]], *, by: Optional[Enum] = ..., flavour: Type, alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> T1: ...
    @overload
    def first[T1, TFlavour](self, selector: SelectorOneType[T, T1], *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @overload
    def first[*TRest](self, selector: SelectorOneType[T, tuple[*TRest]], *, by: Optional[Enum] = ..., flavour: Type[tuple], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> tuple[*TRest]: ...
    @overload
    def first[TFlavour](self, selector: SelectorOneType[T, tuple], *, by: Optional[Enum] = ..., flavour: Type[TFlavour], alias: Optional[AliasType[ClauseInfo[T]]] = ..., **kwargs) -> TFlavour: ...
    @abstractmethod
    def first[TValue, TFlavour, *TRest](
        self,
        selector: Optional[SelectorOneType[T, tuple[TValue, *TRest]]] = lambda: None,
        *,
        flavour: Type[TFlavour] = ...,
        by: Optional[Enum] = ...,
    ): ...

    # endregion

    # region groupby
    @overload
    def groupby[TRepo](self, column: list[SelectCols[T, TRepo]]) -> IStatements[T]: ...
    @overload
    def groupby[TRepo](self, column: SelectCols[T, TRepo]) -> IStatements[T]: ...
    @abstractmethod
    def groupby[TRepo](self, column: list[SelectCols[T, TRepo]] | SelectCols[T, TRepo]) -> IStatements[T]: ...

    # endregion

    @abstractmethod
    def alias[TProp](self, column: SelectCols[T, TProp], alias: AliasType[ClauseInfo[T]]) -> ClauseInfo[T]: ...


class IStatements_two_generic[T, TPool](IStatements[T]):
    @property
    @abstractmethod
    def repository(self) -> BaseRepository[TPool]: ...

    @property
    @abstractmethod
    def query(self) -> str: ...

    @property
    def model(self) -> Type[T]: ...

    # TODOL: add P when wil be possible
    @property
    def models(self) -> tuple: ...
