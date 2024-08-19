from typing import override, Type


from src.common.abstract_classes import AbstractSQLStatements
from src.utils import Table
from src.common.interfaces import IQuery, IRepositoryBase

from src.components.select import ISelect

from .clauses import DeleteQuery
from .clauses import InsertQuery
from .clauses import JoinSelector
from .clauses import LimitQuery
from .clauses import OffsetQuery
from .clauses import OrderQuery
from .clauses import SelectQuery
from .clauses import UpsertQuery
from .clauses import UpdateQuery
from .clauses import WhereCondition

from mysql.connector import MySQLConnection


class MySQLStatements[T: Table](AbstractSQLStatements[T, MySQLConnection]):
    def __init__(self, model: T, repository: IRepositoryBase[MySQLConnection]) -> None:
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

    @property
    @override
    def UPDATE_QUERY(self) -> Type[UpsertQuery]:
        return UpdateQuery

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

    @property
    @override
    def repository(self) -> IRepositoryBase[MySQLConnection]:
        return self._repository
