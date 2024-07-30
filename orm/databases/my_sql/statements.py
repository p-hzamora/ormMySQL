from typing import override, Type


from orm.abstract_model import AbstractSQLStatements
from orm.utils import Table

from orm.interfaces import ISelect, IQuery


from .clauses.joins import JoinSelector
from .clauses.select import SelectQuery
from .clauses.limit import LimitQuery
from .clauses.where_condition import WhereCondition
from .clauses.order import OrderQuery
from .clauses.offset import OffsetQuery
from .clauses.delete import DeleteQuery
from .clauses.insert import InsertQuery
from .clauses.upsert import UpsertQuery

from orm.interfaces import IRepositoryBase


class MySQLStatements[T: Table](AbstractSQLStatements[T]):
    def __init__(self, model: T, repository: IRepositoryBase) -> None:
        super().__init__(model, repository=repository)

    # region Private methods
    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    # endregion

    @property
    @override
    def INSERT_QUERY(self) -> Type[InsertQuery]:
        return InsertQuery

    @property
    @override
    def UPSERT_QUERY(self) -> Type[UpsertQuery]:
        return UpsertQuery

    @override
    @property
    def DELETE_QUERY(self) -> Type[DeleteQuery]:
        return DeleteQuery

    @property
    @override
    def LIMIT_QUERY(self) -> Type[IQuery]:
        return LimitQuery

    @property
    @override
    def OFFSET_QUERY(self) -> Type[IQuery]:
        return OffsetQuery

    @property
    @override
    def JOIN_QUERY(self) -> Type[IQuery]:
        return JoinSelector

    @property
    @override
    def WHERE_QUERY(self) -> Type[IQuery]:
        return WhereCondition

    @property
    @override
    def ORDER_QUERY(self) -> Type[IQuery]:
        return OrderQuery

    @property
    @override
    def SELECT_QUERY(self) -> Type[ISelect]:
        return SelectQuery
