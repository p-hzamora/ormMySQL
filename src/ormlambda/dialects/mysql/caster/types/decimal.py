from typing import Optional
from ormlambda.caster import BaseCaster, Caster
from decimal import Decimal


class DecimalCaster[TType](BaseCaster[Decimal, TType]):
    def __init__(self, value: Decimal, type_value: TType):
        super().__init__(value, type_value)

    def wildcard_to_select(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_where(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    def wildcard_to_insert(self, value: Optional[str] = None) -> str:
        return Caster.PLACEHOLDER if value is None else value

    @property
    @BaseCaster.return_value_if_exists
    def to_database(self) -> Optional[Decimal]:
        return Decimal(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def from_database(self) -> Optional[Decimal]:
        return Decimal(self.value)

    @property
    @BaseCaster.return_value_if_exists
    def string_data(self) -> Optional[str]:
        return str(self.value)
