from typing import Protocol

from ormlambda.sql.clause_info.aggregate_function_base import AggregateFunctionBase
from .clauses import (
    _Count,
    _Delete,
    _GroupBy,
    _Insert,
    _JoinSelector,
    _Limit,
    _Offset,
    _Order,
    _Select,
    _Where,
    _Having,
    _Update,
    _Upsert,
)


class SQLMethods[T, TRepo](Protocol):
    """Protocol base class to create all necessary methods to use Statements class"""

    @staticmethod
    def count(*args, **kwargs) -> _Count[T]: ...
    @staticmethod
    def delete(*args, **kwargs) -> _Delete[T, TRepo]: ...
    @staticmethod
    def groupby(*args, **kwargs) -> _GroupBy: ...
    @staticmethod
    def insert(*args, **kwargs) -> _Insert[T, TRepo]: ...
    @staticmethod
    def joins[**P](*args: P.args, **kwargs: P.kwargs) -> _JoinSelector[T, P]: ...
    @staticmethod
    def limit(*args, **kwargs) -> _Limit: ...
    @staticmethod
    def offset(*args, **kwargs) -> _Offset: ...
    @staticmethod
    def order(*args, **kwargs) -> _Order: ...
    @staticmethod
    def select(*args, **kwargs) -> _Select[T]: ...
    @staticmethod
    def where(*args, **kwargs) -> _Where: ...
    @staticmethod
    def having(*args, **kwargs) -> _Having: ...
    @staticmethod
    def update(*args, **kwargs) -> _Update[T, TRepo]: ...
    @staticmethod
    def upsert(*args, **kwargs) -> _Upsert[T, TRepo]: ...
    @staticmethod
    def max(*args, **kwargs) -> AggregateFunctionBase[T]: ...
    @staticmethod
    def min(*args, **kwargs) -> AggregateFunctionBase[T]: ...
    @staticmethod
    def sum(*args, **kwargs) -> AggregateFunctionBase[T]: ...
    @staticmethod
    def concat(*args, **kwargs) -> AggregateFunctionBase[T]: ...
