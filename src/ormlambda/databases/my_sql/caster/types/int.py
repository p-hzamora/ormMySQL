from typing import Optional
from ormlambda.caster import BaseCaster, PLACEHOLDER


class IntegerCaster[TType](BaseCaster[int, TType]):
    def __init__(self, value: int, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value:str=PLACEHOLDER) -> str:
        return value

    def wildcard_to_where(self, value:str=PLACEHOLDER) -> str:
        return value

    def wildcard_to_insert(self, value:str=PLACEHOLDER) -> str:
        return value

    @property
    @BaseCaster.return_value_if_exists
    def to_database(self) -> Optional[int]:
        return int(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[int]:
        return int(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        return str(self.value)
