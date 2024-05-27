from orm import (
    Column,
    Table,
    ModelBase,
    IRepositoryBase,
)

from datetime import datetime


class Actor(Table):
    __table_name__ = "actor"

    actor_id: int = Column[int](is_primary_key=True)
    first_name: str = Column[str]()
    last_name: str = Column[str]()
    last_update: datetime = Column[datetime]()


class ActorModel(ModelBase[Actor]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Actor, repository=repository)
