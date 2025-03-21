from __future__ import annotations
from typing import Any, Callable, Concatenate, Optional, Type, overload, TYPE_CHECKING
from enum import Enum
from abc import abstractmethod, ABC


from ormlambda.common.enums import JoinType

if TYPE_CHECKING:
    from ormlambda.repository import BaseRepository
    from ormlambda import Table
    from ormlambda.sql.clause_info import IAggregate
    from ormlambda.sql.types import TupleJoinType
    from ormlambda.databases.my_sql.join_context import JoinContext

from ..types import (
    OrderTypes,
    Select1,
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
)


class IStatements[T: Table, **P](ABC):
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

    @abstractmethod
    def update(self, dicc: dict[str | property, Any]) -> None: ...

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
    def count(
        self,
        selection: Callable[[T], tuple] = lambda x: "*",
        alias_clause="count",
        execute: bool = False,
    ) -> Optional[IStatements[T]]: ...

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
    def where[LProp, RTable, RProp](self, conditions: Callable[[T], WhereTypes[T, LProp, RTable, RProp]]) -> IStatements[T, P]: ...

    @abstractmethod
    def where[LProp, RTable, RProp](self, conditions: WhereTypes[T, LProp, RTable, RProp] = None) -> IStatements[T, P]: ...

    # endregion
    # region order
    @overload
    def order[TValue](self, _lambda_col: Callable[[T], TValue]) -> IStatements[T]: ...
    @overload
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderTypes) -> IStatements[T]: ...
    @abstractmethod
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderTypes) -> IStatements[T]: ...

    # endregion
    # region concat
    @overload
    def concat[P](self, selector: Callable[[T], tuple[P]]) -> IAggregate: ...

    # endregion
    # region max
    @overload
    def max[TProp](
        self,
        column: Callable[[T], TProp],
        alias: bool = ...,
        alias_name: Optional[str] = ...,
    ) -> TProp: ...
    # endregion
    # region min
    @overload
    def min[TProp](
        self,
        column: Callable[[T], TProp],
        alias: bool = ...,
        alias_name: Optional[str] = ...,
    ) -> TProp: ...
    # endregion
    # region sum
    @overload
    def sum[TProp](
        self,
        column: Callable[[T], TProp],
        alias: bool = ...,
        alias_name: Optional[str] = ...,
    ) -> TProp: ...

    @overload
    def join[FKTable](self, joins: TupleJoinType[FKTable] | tuple[*TupleJoinType[FKTable]]) -> JoinContext[tuple[*TupleJoinType[FKTable]]]: ...

    # endregion
    # region select
    @overload
    def select(self) -> Select1[T]: ...
    @overload
    def select[T1](self, selector: Callable[[T], T1], *, by: Optional[Enum] = ...) -> Select1[T1]: ...
    @overload
    def select[T1](self, selector: Callable[[T], tuple[T1]], *, by: Optional[Enum] = ...) -> Select1[T1]: ...
    @overload
    def select[T1, T2](self, selector: Callable[Concatenate[T, P], tuple[T1, T2]], *, by: Optional[Enum] = ...) -> Select2[T1, T2]: ...
    @overload
    def select[T1, T2, T3](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3]], *, by: Optional[Enum] = ...) -> Select3[T1, T2, T3]: ...
    @overload
    def select[T1, T2, T3, T4](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4]], *, by: Optional[Enum] = ...) -> Select4[T1, T2, T3, T4]: ...
    @overload
    def select[T1, T2, T3, T4, T5](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5]], *, by: Optional[Enum] = ...) -> Select5[T1, T2, T3, T4, T5]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5, T6]], *, by: Optional[Enum] = ...) -> Select6[T1, T2, T3, T4, T5, T6]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5, T6, T7]], *, by: Optional[Enum] = ...) -> Select7[T1, T2, T3, T4, T5, T6, T7]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5, T6, T7, T8]], *, by: Optional[Enum] = ...) -> Select8[T1, T2, T3, T4, T5, T6, T7, T8]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]], *, by: Optional[Enum] = ...) -> Select9[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](self, selector: Callable[Concatenate[T, P], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]], *, by: Optional[Enum] = ...) -> Select10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...

    @overload
    def select[TFlavour](self, selector: Optional[Callable[Concatenate[T, P], tuple]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour], by: Optional[Enum] = ..., **kwargs) -> TFlavour: ...
    @overload
    def select[TRes](self, selector: Optional[Callable[Concatenate[T, P], TRes]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[TRes, ...]: ...
    @overload
    def select[TRes](self, selector: Optional[Callable[Concatenate[T, P], tuple[TRes]]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[TRes, ...]: ...
    @overload
    def select[*TRes](self, selector: Optional[Callable[Concatenate[T, P], tuple[*TRes]]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[tuple[*TRes]]: ...
    @overload
    def select[TFlavour](self, selector: Optional[Callable[Concatenate[T, P], tuple]] = ..., *, flavour: Type[TFlavour], by: Optional[Enum] = ..., **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def select[TValue, TFlavour, P](self, selector: Optional[Callable[Concatenate[T, P], tuple[TValue, P]]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour] = ..., by: JoinType = ..., **kwargs): ...

    # endregion
    # region select_one
    @overload
    def select_one(self) -> T: ...
    @overload
    def select_one[TFlavour](self, *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> TFlavour: ...
    @overload
    def select_one[T1](self, selector: Callable[Concatenate[T, P], tuple[T1]], *, by: Optional[Enum] = ...) -> T1: ...
    @overload
    def select_one[*TRes](self, selector: Callable[Concatenate[T, P], tuple[*TRes]], *, by: Optional[Enum] = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[T1](self, selector: Callable[Concatenate[T, P], tuple[T1]], *, by: Optional[Enum] = ..., flavour: Type) -> T1: ...
    @overload
    def select_one[T1, TFlavour](self, selector: Callable[Concatenate[T, P], T1], *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> T1: ...
    @overload
    def select_one[**P](self, selector: Callable[Concatenate[T, P], tuple[P]], *, by: Optional[Enum] = ..., flavour: Type[tuple]) -> tuple[P]: ...
    @overload
    def select_one[TFlavour](self, selector: Callable[Concatenate[T, P], tuple], *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> TFlavour: ...
    @abstractmethod
    def select_one[TValue, TFlavour, **P](
        self,
        selector: Optional[Callable[Concatenate[T, P], tuple[TValue, P]]] = lambda: None,
        *,
        flavour: Type[TFlavour] = ...,
        by: Optional[Enum] = ...,
    ): ...

    # endregion
    # region group_by
    @abstractmethod
    def group_by[TRepo](self, column: Callable[Concatenate[T, P], TRepo]) -> IStatements[T, P]: ...

    # endregion

    @abstractmethod
    def alias(self, column: Callable[Concatenate[T, P], Any], alias: str) -> IStatements[T, P]: ...


class IStatements_two_generic[T, TPool](IStatements[T, TPool]):
    @property
    @abstractmethod
    def repository(self) -> BaseRepository[TPool]: ...

    @property
    def query(self) -> str: ...

    @property
    def model(self) -> Type[T]: ...

    # TODOL: add P when wil be possible
    @property
    def models(self) -> tuple: ...
