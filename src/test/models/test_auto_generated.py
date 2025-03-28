from ormlambda import (
    Column,
    Table,
    BaseModel,
)

from datetime import datetime
from ormlambda.repository import IRepositoryBase


class TableWithAutoGenerated(Table):
    __table_name__ = "__test_table__AUTOGENERATED"

    Col_pk_auto_increment: int = Column(int, is_primary_key=True, is_auto_increment=True)
    Col_auto_generated: datetime = Column(datetime, is_auto_generated=True)
    Col3: int
    Col4: int


class TestTableAUTOModel(BaseModel[TableWithAutoGenerated]):
    def __new__[TRepo](cls, repository: IRepositoryBase):
        return super().__new__(cls, TableWithAutoGenerated, repository)
