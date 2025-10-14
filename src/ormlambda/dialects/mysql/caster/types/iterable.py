from typing import Optional
from ormlambda.caster import BaseCaster, Caster
from .json import JsonCaster


class IterableCaster[TType](JsonCaster[TType]):
    def __init__(self, value: bytes, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_where(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_insert(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    @property
    @BaseCaster.return_value_if_exists
    def to_database(self) -> Optional[bytes]:
        return super().to_database

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[bytes]:
        return super().from_database

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        value = tuple(self.value) if not isinstance(self.value, tuple) else self.value

        if len(value) == 1:
            return f"({value[0]})"
        return str(value)
