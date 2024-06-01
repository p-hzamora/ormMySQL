from orm import (
    Column,
    Table,
    ModelBase,
    IRepositoryBase,
)

from datetime import datetime


class Actor(Table):
    __table_name__:str = "actor"

    actor_id: int = Column[int](is_primary_key=True)
    first_name: str
    last_name: str
    last_update: datetime


class ActorModel(ModelBase[Actor]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Actor, repository=repository)
