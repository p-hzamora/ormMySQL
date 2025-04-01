import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Column, Table, BaseModel, BaseRepository

from datetime import datetime


class Actor(Table):
    __table_name__ = "actor"

    actor_id: str = Column(str, is_primary_key=True)
    first_name: str
    last_name: str
    last_update: datetime


class ActorModel(BaseModel[Actor]):
    def __new__(cls, repository: BaseRepository):
        return super().__new__(cls, Actor, repository)
