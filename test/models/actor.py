from orm import (
    Column,
    Table,
    ModelBase,
)

from datetime import datetime

from orm.common.interfaces import IRepositoryBase

class Actor(Table):
    __table_name__ = "actor"

    actor_id: int = Column[int](is_primary_key=True)
    first_name: str
    last_name: str
    last_update: datetime



class ActorModel(ModelBase[Actor]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Actor, repository=repository)
