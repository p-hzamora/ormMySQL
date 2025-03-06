from typing import Optional
from ormlambda.caster import BaseCaster, PLACEHOLDER


class BytesCaster[TType](BaseCaster[bytes, TType]):
    def __init__(self, value: bytes, type_value: TType):
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
    def to_database(self) -> Optional[bytes]:
        return bytes(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[bytes]:
        return bytes(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        return str(self.value)
