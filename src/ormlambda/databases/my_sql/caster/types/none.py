from types import NoneType
from ormlambda.caster import BaseCaster, PLACEHOLDER


class NoneTypeCaster[TType](BaseCaster[NoneType, TType]):
    def __init__(self, value: NoneType, type_value: TType):
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
