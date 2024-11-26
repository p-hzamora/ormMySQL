import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda import (
    IRepositoryBase,
    Column,
    Table,
    BaseModel,
)

from datetime import datetime


class Actor(Table):
    __table_name__ = "actor"

    actor_id: str = Column(str, is_primary_key=True)
    first_name: str
    last_name: str
    last_update: datetime


class ActorModel(BaseModel[Actor]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Actor, repository)
