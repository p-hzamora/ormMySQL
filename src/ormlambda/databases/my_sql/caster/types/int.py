from typing import Optional
from ormlambda.caster import BaseCaster, PLACEHOLDER


class IntegerCaster[TType](BaseCaster[int, TType]):
    def __init__(self, value: int, type_value: TType):
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
