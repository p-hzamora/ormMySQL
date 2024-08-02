from orm import (
    Column,
    Table,
    ModelBase,
)

from datetime import datetime

from orm.common.interfaces import IRepositoryBase
from orm.common.interfaces.IStatements import IStatements_two_generic


class Actor(Table):
    __table_name__ = "actor"

    actor_id: int = Column[int](is_primary_key=True)
    first_name: str
    last_name: str
    last_update: datetime


class ActorModel(ModelBase[Actor]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]) -> IStatements_two_generic[Actor, TRepo]:
        return super().__new__(cls, Actor, repository)
