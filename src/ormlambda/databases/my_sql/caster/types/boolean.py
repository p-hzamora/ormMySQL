from typing import Optional
from ormlambda.caster import BaseCaster, Caster


class BooleanCaster[TType](BaseCaster[bool, TType]):
    """
    MySQL uses 0/1 for booleans stored in TINYINT
    """

    def __init__(self, value: bool, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_where(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_insert(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    @property
    @BaseCaster.return_value_if_exists
    def to_database(self) -> Optional[int]:
        return 1 if self.value else 0

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[bool]:
        return bool(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        return str(bool(self.value))
