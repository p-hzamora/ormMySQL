from __future__ import annotations
from typing import Any, Callable, Iterable, Optional, Literal, Type, Union, overload, TYPE_CHECKING
from enum import Enum
from abc import abstractmethod, ABC
import enum

from .IRepositoryBase import IRepositoryBase
from ormlambda.common.enums import JoinType

if TYPE_CHECKING:
    from ormlambda import Table
    from .IAggregate import IAggregate


class OrderType(enum.Enum):
    ASC = "ASC"
    DESC = "DESC"


type OrderTypes = Literal["ASC", "DESC"] | OrderType | Iterable[OrderType]


type Tuple[T] = tuple[T, ...]

type SelectRes1[T1] = tuple[Tuple[T1]]
type SelectRes2[T1, T2] = tuple[*SelectRes1[T1], Tuple[T2]]
type SelectRes3[T1, T2, T3] = tuple[*SelectRes2[T1, T2], Tuple[T3]]
type SelectRes4[T1, T2, T3, T4] = tuple[*SelectRes3[T1, T2, T3], Tuple[T4]]
type SelectRes5[T1, T2, T3, T4, T5] = tuple[*SelectRes4[T1, T2, T3, T4], Tuple[T5]]
type SelectRes6[T1, T2, T3, T4, T5, T6] = tuple[*SelectRes5[T1, T2, T3, T4, T5], Tuple[T6]]
type SelectRes7[T1, T2, T3, T4, T5, T6, T7] = tuple[*SelectRes6[T1, T2, T3, T4, T5, T6], Tuple[T7]]
type SelectRes8[T1, T2, T3, T4, T5, T6, T7, T8] = tuple[*SelectRes7[T1, T2, T3, T4, T5, T6, T7], Tuple[T8]]
type SelectRes9[T1, T2, T3, T4, T5, T6, T7, T8, T9] = tuple[*SelectRes8[T1, T2, T3, T4, T5, T6, T7, T8], Tuple[T9]]
type SelectRes10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10] = tuple[*SelectRes9[T1, T2, T3, T4, T5, T6, T7, T8, T9], Tuple[T10]]


type WhereCondition[T, T1] = Callable[[T, T1], bool]
type JoinCondition[T, T1] = tuple[T1, WhereCondition[T, T1]]

type TupleJoins1[T, T1] = tuple[JoinCondition[T, T1]]
type TupleJoins2[T, T1, T2] = tuple[*TupleJoins1[T, T1], JoinCondition[T, T2]]
type TupleJoins3[T, T1, T2, T3] = tuple[*TupleJoins2[T, T1, T2], JoinCondition[T, T3]]
type TupleJoins4[T, T1, T2, T3, T4] = tuple[*TupleJoins3[T, T1, T2, T3], JoinCondition[T, T4]]
type TupleJoins5[T, T1, T2, T3, T4, T5] = tuple[*TupleJoins4[T, T1, T2, T3, T4], JoinCondition[T, T5]]
type TupleJoins6[T, T1, T2, T3, T4, T5, T6] = tuple[*TupleJoins5[T, T1, T2, T3, T4, T5], JoinCondition[T, T6]]


# TODOH: This var is duplicated from 'src\ormlambda\databases\my_sql\clauses\create_database.py'
TypeExists = Literal["fail", "replace", "append"]

type WhereTypes[T, *Ts] = Union[Callable[[T, *Ts], bool], Iterable[Callable[[T, *Ts], bool]]]


class IStatements[T, *Ts](ABC):
    @abstractmethod
    def create_table(self, if_exists: TypeExists) -> None: ...

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
        selection: Callable[[T], property],
        alias: bool = ...,
        alias_name: Optional[str] = ...,
    ) -> int: ...

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
    def where(self, conditions: Iterable[Callable[[T, *Ts], bool]]) -> IStatements[T, *Ts]:
        """
        This method creates where clause by passing the Iterable in lambda function
        EXAMPLE
        -
        mb = BaseModel()
        mb.where(lambda a: (a.city, ConditionType.REGEXP, r"^B"))
        """
        ...

    @overload
    def where(self, conditions: Callable[[T, *Ts], bool], **kwargs) -> IStatements[T, *Ts]:
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
    def where(self, conditions: WhereTypes[T, *Ts] = lambda: None, **kwargs) -> IStatements[T, *Ts]: ...

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
    def concat[*Ts](self, selector: Callable[[T], tuple[*Ts]]) -> IAggregate[T]: ...

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

    # endregion
    # region join

    @overload
    def join[T1](self, joins: JoinCondition[T, T1]) -> IStatements[T, T1]: ...
    @overload
    def join[T1](self, joins: TupleJoins1[T, T1]) -> IStatements[T, T1]: ...
    @overload
    def join[T1, T2](self, joins: TupleJoins2[T, T1, T2]) -> IStatements[T, T1, T2]: ...
    @overload
    def join[T1, T2, T3](self, joins: TupleJoins3[T, T1, T2, T3]) -> IStatements[T, T1, T2, T3]: ...
    @overload
    def join[T1, T2, T3, T4](self, joins: TupleJoins4[T, T1, T2, T3, T4]) -> IStatements[T, T1, T2, T3, T4]: ...
    @overload
    def join[T1, T2, T3, T4, T5](self, joins: TupleJoins5[T, T1, T2, T3, T4, T5]) -> IStatements[T, T1, T2, T3, T4, T5]: ...
    @overload
    def join[T1, T2, T3, T4, T5, T6](self, joins: TupleJoins6[T, T1, T2, T3, T4, T5, T6]) -> IStatements[T, T1, T2, T3, T4, T5, T6]: ...

    @abstractmethod
    def join[*FKTables](self, joins) -> IStatements[T, *FKTables]: ...

    # endregion
    # region select
    @overload
    def select(self) -> SelectRes1[T]: ...
    @overload
    def select[T1](self, selector: Callable[[T], T1], *, by: Optional[Enum] = ...) -> SelectRes1[T1]: ...
    @overload
    def select[T1](self, selector: Callable[[T], tuple[T1]], *, by: Optional[Enum] = ...) -> SelectRes1[T1]: ...
    @overload
    def select[T1, T2](self, selector: Callable[[T, *Ts], tuple[T1, T2]], *, by: Optional[Enum] = ...) -> SelectRes2[T1, T2]: ...
    @overload
    def select[T1, T2, T3](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3]], *, by: Optional[Enum] = ...) -> SelectRes3[T1, T2, T3]: ...
    @overload
    def select[T1, T2, T3, T4](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4]], *, by: Optional[Enum] = ...) -> SelectRes4[T1, T2, T3, T4]: ...
    @overload
    def select[T1, T2, T3, T4, T5](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5]], *, by: Optional[Enum] = ...) -> SelectRes5[T1, T2, T3, T4, T5]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5, T6]], *, by: Optional[Enum] = ...) -> SelectRes6[T1, T2, T3, T4, T5, T6]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5, T6, T7]], *, by: Optional[Enum] = ...) -> SelectRes7[T1, T2, T3, T4, T5, T6, T7]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5, T6, T7, T8]], *, by: Optional[Enum] = ...) -> SelectRes8[T1, T2, T3, T4, T5, T6, T7, T8]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]], *, by: Optional[Enum] = ...) -> SelectRes9[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...
    @overload
    def select[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](self, selector: Callable[[T, *Ts], tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]], *, by: Optional[Enum] = ...) -> SelectRes10[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...

    @overload
    def select[TFlavour](self, selector: Optional[Callable[[T, *Ts], tuple]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour], by: Optional[Enum] = ..., **kwargs) -> TFlavour: ...
    @overload
    def select[TRes](self, selector: Optional[Callable[[T, *Ts], TRes]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[TRes, ...]: ...
    @overload
    def select[TRes](self, selector: Optional[Callable[[T, *Ts], tuple[TRes]]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[TRes, ...]: ...
    @overload
    def select[*TRes](self, selector: Optional[Callable[[T, *Ts], tuple[*TRes]]] = ..., *, flavour: Type[tuple], by: Optional[Enum] = ..., **kwargs) -> tuple[tuple[*TRes]]: ...
    @overload
    def select[TFlavour](self, selector: Optional[Callable[[T, *Ts], tuple]] = ..., *, flavour: Type[TFlavour], by: Optional[Enum] = ..., **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def select[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T, *Ts], tuple[TValue, *Ts]]] = ..., *, cast_to_tuple: bool = ..., flavour: Type[TFlavour] = ..., by: JoinType = ..., **kwargs): ...

    # endregion
    # region select_one
    @overload
    def select_one(self) -> T: ...
    @overload
    def select_one[TFlavour](self, *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> TFlavour: ...
    @overload
    def select_one[T1](self, selector: Callable[[T, *Ts], tuple[T1]], *, by: Optional[Enum] = ...) -> T1: ...
    @overload
    def select_one[*TRes](self, selector: Callable[[T, *Ts], tuple[*TRes]], *, by: Optional[Enum] = ...) -> tuple[*TRes]: ...
    @overload
    def select_one[T1](self, selector: Callable[[T, *Ts], tuple[T1]], *, by: Optional[Enum] = ..., flavour: Type) -> T1: ...
    @overload
    def select_one[T1, TFlavour](self, selector: Callable[[T, *Ts], T1], *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> T1: ...
    @overload
    def select_one[*Ts](self, selector: Callable[[T, *Ts], tuple[*Ts]], *, by: Optional[Enum] = ..., flavour: Type[tuple]) -> tuple[*Ts]: ...
    @overload
    def select_one[TFlavour](self, selector: Callable[[T, *Ts], tuple], *, by: Optional[Enum] = ..., flavour: Type[TFlavour]) -> TFlavour: ...
    @abstractmethod
    def select_one[TValue, TFlavour, *Ts](self, selector: Optional[Callable[[T, *Ts], tuple[TValue, *Ts]]] = lambda: None, *, flavour: Type[TFlavour] = ..., by: Optional[Enum] = ...): ...

    # endregion
    # region group_by
    @abstractmethod
    def group_by[TRepo](self, column: Callable[[T, *Ts], TRepo]) -> IStatements[T, *Ts]: ...

    # endregion

    @abstractmethod
    def _build(self) -> str: ...


class IStatements_two_generic[T: Table, *Ts, TRepo](IStatements[T, *Ts]):
    @property
    @abstractmethod
    def repository(self) -> IRepositoryBase[TRepo]: ...

    @property
    def query(self) -> str: ...

    @property
    def model(self) -> Type[T]: ...

    @property
    def models(self) -> tuple[*Ts]: ...
