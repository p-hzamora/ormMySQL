from types import NoneType
from typing import Optional
from ormlambda.caster import BaseCaster, Caster


class NoneTypeCaster[TType](BaseCaster[NoneType, TType]):
    def __init__(self, value: NoneType, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_where(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_insert(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    # TODOL: cheched if it's right
    @property
    def to_database(self) -> None:
        return None

    # TODOL: cheched if it's right
    @property
    def from_database(self) -> None:
        return None

    @property
    def string_data(self) -> str:
        return "NULL"
