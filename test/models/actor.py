from orm import (
    Column,
    Table,
    nameof,
    ModelBase,
    IRepositoryBase,
)

from datetime import datetime


class Actor(Table):
    __table_name__ = "actor"

    def __init__(self, actor_id: int, first_name: str, last_name: str, last_update: datetime) -> None:
        self._actor_id: Column[int] = Column(nameof(actor_id), actor_id, is_primary_key=True)
        self._first_name: Column[str] = Column(nameof(first_name), first_name)
        self._last_name: Column[str] = Column(nameof(last_name), last_name)
        self._last_update: Column[datetime] = Column(nameof(last_update), last_update)

    @property
    def actor(self) -> int:
        return self._actor_id.column_value

    @actor.setter
    def actor(self, value: int) -> None:
        self._actor_id.column_value = value

    @property
    def first_name(self) -> str:
        return self._first_name.column_value

    @first_name.setter
    def first_name(self, value: str) -> None:
        self._first_name.column_value = value

    @property
    def last_name(self) -> str:
        return self._last_name.column_value

    @last_name.setter
    def last_name(self, value: str) -> None:
        self._last_name.column_value = value

    @property
    def last_update(self) -> str:
        return self._last_update.column_value

    @last_update.setter
    def last_update(self, value: str) -> None:
        self._last_update.column_value = value


class ActorModel(ModelBase[Actor]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Actor, repository=repository)
