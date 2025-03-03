from ormlambda.caster import BaseCaster, PLACEHOLDER
from datetime import datetime


class DatetimeCaster[TType](BaseCaster[datetime, TType]):
    def __init__(self, value: datetime, type_value: TType):
        super().__init__(value, type_value)

    @property
    def wildcard_to_select(self) -> str:
        return PLACEHOLDER

    @property
    def wildcard_to_where(self) -> str:
        return PLACEHOLDER

    @property
    def wildcard_to_insert(self) -> str:
        return PLACEHOLDER

    @property
    def to_database(self) -> datetime:
        return self.value

    @property
    def from_database(self) -> datetime:
        return self.value
