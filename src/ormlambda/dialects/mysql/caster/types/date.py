from typing import Optional
from ormlambda.caster import BaseCaster, Caster
from datetime import datetime
from .string import StringCaster


class DateCaster[TType](BaseCaster[datetime, TType]):
    def __init__(self, value: datetime, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_where(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_insert(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    @property
    @BaseCaster.return_value_if_exists
    def to_database(self) -> Optional[datetime]:
        return self.value

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[datetime]:
        return self.value

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        datetime_string = self.value.strftime(r"%Y-%m-%d")
        return StringCaster(datetime_string, str).string_data
