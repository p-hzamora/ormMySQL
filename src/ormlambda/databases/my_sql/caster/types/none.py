from types import NoneType
from ormlambda.caster import BaseCaster, PLACEHOLDER


class NoneTypeCaster[TType](BaseCaster[NoneType, TType]):
    def __init__(self, value: NoneType, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value:str=PLACEHOLDER) -> str:
        return value

    def wildcard_to_where(self, value:str=PLACEHOLDER) -> str:
        return value

    def wildcard_to_insert(self, value:str=PLACEHOLDER) -> str:
        return value

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
