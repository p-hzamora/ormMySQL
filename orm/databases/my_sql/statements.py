from typing import override, Type


from orm.abstract_model import AbstractSQLStatements
from orm.utils import Table
from orm.common.interfaces import IQuery, IRepositoryBase
from orm.components.create_database import CreateDatabaseBase
from orm.components.drop_database import DropDatabaseBase
from orm.components.drop_table import DropTableBase

from orm.components.select import ISelect

from .clauses import CreateDatabase
from .clauses import DeleteQuery
from .clauses import DropDatabase
from .clauses import DropTable
from .clauses import InsertQuery
from .clauses import JoinSelector
from .clauses import LimitQuery
from .clauses import OffsetQuery
from .clauses import OrderQuery
from .clauses import SelectQuery
from .clauses import UpsertQuery
from .clauses import WhereCondition

from .repository import MySQLRepository


class MySQLStatements[T: Table](AbstractSQLStatements[T, MySQLRepository]):
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

    @property
    @override
    def DropDatabase(self) -> Type[DropDatabaseBase]:
        return DropDatabase

    @property
    @override
    def CreateDatabase(self) -> Type[CreateDatabaseBase]:
        return CreateDatabase

    @property
    @override
    def DropTable(self)->Type[DropTableBase]:
        return DropTable