from __future__ import annotations
from typing import Any, Callable, Iterable, Optional, Literal, Type, overload, TYPE_CHECKING
from enum import Enum
from abc import abstractmethod, ABC

from .IRepositoryBase import IRepositoryBase
from ormlambda.common.enums import JoinType

if TYPE_CHECKING:
    from ormlambda import Table

OrderType = Literal["ASC", "DESC"]

# TODOH: This var is duplicated from 'src\ormlambda\databases\my_sql\clauses\create_database.py'
TypeExists = Literal["fail", "replace", "append"]


class IStatements[T: Table](ABC):
    @abstractmethod
    def create_table(self, if_exists: TypeExists) -> None: ...

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
    def count(self) -> int: ...

    # endregion

    # region delete
    @overload
    def delete(self) -> None: ...

    @overload
    def delete(self, instance: T) -> None: ...

    @overload
    def delete(self, instance: list[T]) -> None: ...
    @abstractmethod
    def delete(self, instance: Optional[T | list[T]] = None) -> None: ...

    # endregion

    # region join
    @abstractmethod
    def join(self, table_left: Table, table_right: Table, *, by: str) -> IStatements[T]: ...

    # endregion

    # region where
    @overload
    def where(self, lambda_: Callable[[T], bool]) -> IStatements[T]:
        """
        This method creates where clause by passing the lambda's condition

        EXAMPLE
        -
        mb = BaseModel()
        mb.where(lambda a: 10 <= a.city_id <= 100)
        """
        ...

    @overload
    def where(self, lambda_: Callable[[T], Iterable]) -> IStatements[T]:
        """
        This method creates where clause by passing the Iterable in lambda function
        EXAMPLE
        -
        mb = BaseModel()
        mb.where(lambda a: (a.city, ConditionType.REGEXP, r"^B"))
        """
        ...

    @overload
    def where(self, lambda_: Callable[[T], bool], **kwargs) -> IStatements[T]:
        """
        PARAM
        -

        -kwargs: Use this when you need to replace variables inside a lambda method. When working with lambda methods, all variables will be replaced by their own variable names. To avoid this, we need to pass key-value parameters  to specify which variables we want to replace with their values.

        EXAMPLE
        -
        mb = BaseModel()

        external_data = "
        mb.where(lambda a: a.city_id > external_data)
        """
        ...

    @abstractmethod
    def where(self, lambda_: Callable[[T], bool] = lambda: None, **kwargs) -> IStatements[T]: ...

    # endregion

    # region order
    @overload
    def order[TValue](self, _lambda_col: Callable[[T], TValue]) -> IStatements[T]: ...
    @overload
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderType) -> IStatements[T]: ...
    @abstractmethod
    def order[TValue](self, _lambda_col: Callable[[T], TValue], order_type: OrderType) -> IStatements[T]: ...

    # endregion

    # region select
    @overload
    def select(self) -> tuple[T, ...]: ...
    @overload
    def select[T1](self, selector: Callable[[T], T1], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...]]: ...
    @overload
    def select[T1](self, selector: Callable[[T], tuple[T1]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...]]: ...
    @overload
    def select[T1, T2](self, selector: Callable[[T], tuple[T1, T2]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...]]: ...
    @overload
    def select[T1, T2, T3](self, selector: Callable[[T], tuple[T1, T2, T3]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...]]: ...
    @overload
    def select[T1, T2, T3, T4](self, selector: Callable[[T], tuple[T1, T2, T3, T4]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5](self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6](self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5, T6]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...], tuple[T6, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7](self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5, T6, T7]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...], tuple[T6, ...], tuple[T7, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8](self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5, T6, T7, T8]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...], tuple[T6, ...], tuple[T7, ...], tuple[T8, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9](
        self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]], *, by: Optional[Enum] = JoinType.INNER_JOIN
    ) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...], tuple[T6, ...], tuple[T7, ...], tuple[T8, ...], tuple[T9, ...]]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](
        self, selector: Callable[[T], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]], *, by: Optional[Enum] = JoinType.INNER_JOIN
    ) -> tuple[tuple[T1, ...], tuple[T2, ...], tuple[T3, ...], tuple[T4, ...], tuple[T5, ...], tuple[T6, ...], tuple[T7, ...], tuple[T8, ...], tuple[T9, ...], tuple[T10, ...]]: ...
    @overload
    def select[Ts](self, selector: Optional[Callable[[T], Ts]] = None, *, flavour: Type[tuple], by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[Ts, ...]: ...
    @overload
    def select[Ts](self, selector: Optional[Callable[[T], tuple[Ts]]] = None, *, flavour: Type[tuple], by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[Ts, ...]: ...
    @overload
    def select[*Ts](self, selector: Optional[Callable[[T], tuple[*Ts]]] = None, *, flavour: Type[tuple], by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[tuple[*Ts]]: ...
    @overload
    def select[TFlavour](self, selector: Optional[Callable[[T], tuple]] = None, *, flavour: Type[TFlavour], by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[TFlavour]: ...
    @abstractmethod
    def select[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Type[TFlavour] = None, by: JoinType = JoinType.INNER_JOIN): ...

    # endregion

    # region select_one
    @overload
    def select_one(self) -> T: ...
    @overload
    def select_one[TFlavour](self, *, by: Optional[Enum] = JoinType.INNER_JOIN, flavour: Type[TFlavour]) -> TFlavour: ...
    @overload
    def select_one[T1](self, selector: Callable[[T], tuple[T1]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> T1: ...
    @overload
    def select_one[*Ts](self, selector: Callable[[T], tuple[*Ts]], *, by: Optional[Enum] = JoinType.INNER_JOIN) -> tuple[*Ts]: ...
    @overload
    def select_one[T1](self, selector: Callable[[T], tuple[T1]], *, by: Optional[Enum] = JoinType.INNER_JOIN, flavour: Type) -> T1: ...
    @overload
    def select_one[T1, TFlavour](self, selector: Callable[[T], T1], *, by: Optional[Enum] = JoinType.INNER_JOIN, flavour: Type[TFlavour]) -> T1: ...
    @overload
    def select_one[*Ts](self, selector: Callable[[T], tuple[*Ts]], *, by: Optional[Enum] = JoinType.INNER_JOIN, flavour: Type[tuple]) -> tuple[*Ts]: ...
    @overload
    def select_one[TFlavour](self, selector: Callable[[T], tuple], *, by: Optional[Enum] = JoinType.INNER_JOIN, flavour: Type[TFlavour]) -> TFlavour: ...
    @abstractmethod
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Type[TFlavour] = None, by: Optional[Enum] = JoinType.INNER_JOIN): ...

    # endregion

    @abstractmethod
    def build(self) -> str: ...


class IStatements_two_generic[T: Table, TRepo](IStatements[T]):
    @property
    @abstractmethod
    def repository(self) -> IRepositoryBase[TRepo]: ...
