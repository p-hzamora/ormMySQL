from ormlambda.caster.caster import Caster
from ormlambda.sql.sql_methods import SQLMethods
from .clauses import Insert

from ormlambda.sql.clauses import (
    _JoinSelector as JoinSelector,
    _Delete as Delete,
    _Limit as Limit,
    _Offset as Offset,
    _Order as Order,
    _Select as Select,
    _Upsert as Upsert,
    _Update as Update,
    _Where as Where,
    _Having as Having,
    _Count as Count,
    _GroupBy as GroupBy,
)
from .functions import (
    Concat,
    Max,
    Min,
    Sum,
)


class SQLiteMethods(SQLMethods):
    def __init__(self):
        Caster.set_placeholder("?")

    # region clauses
    @staticmethod
    def count(*args, **kwargs) -> Count:
        return Count(*args, **kwargs)

    @staticmethod
    def delete(*args, **kwargs) -> Delete:
        return Delete(*args, **kwargs)

    @staticmethod
    def groupby(*args, **kwargs) -> GroupBy:
        return GroupBy(*args, **kwargs)

    @staticmethod
    def insert(*args, **kwargs) -> Insert:
        return Insert(*args, **kwargs)

    @staticmethod
    def joins(*args, **kwargs) -> JoinSelector:
        return JoinSelector(*args, **kwargs)

    @staticmethod
    def limit(*args, **kwargs) -> Limit:
        return Limit(*args, **kwargs)

    @staticmethod
    def offset(*args, **kwargs) -> Offset:
        return Offset(*args, **kwargs)

    @staticmethod
    def order(*args, **kwargs) -> Order:
        return Order(*args, **kwargs)

    @staticmethod
    def select(*args, **kwargs) -> Select:
        return Select(*args, **kwargs)

    @staticmethod
    def where(*args, **kwargs) -> Where:
        return Where(*args, **kwargs)

    @staticmethod
    def having(*args, **kwargs) -> Having:
        return Having(*args, **kwargs)

    @staticmethod
    def update(*args, **kwargs) -> Update:
        return Update(*args, **kwargs)

    @staticmethod
    def upsert(*args, **kwargs) -> Upsert:
        return Upsert(*args, **kwargs)

    # endregion
    # region functions
    @staticmethod
    def concat(*args, **kwargs) -> Concat:
        return Concat(*args, **kwargs)

    @staticmethod
    def max(*args, **kwargs) -> Max:
        return Max(*args, **kwargs)

    @staticmethod
    def min(*args, **kwargs) -> Min:
        return Min(*args, **kwargs)

    @staticmethod
    def sum(*args, **kwargs) -> Sum:
        return Sum(*args, **kwargs)

    # endregion
