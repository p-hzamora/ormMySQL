from ormlambda.caster import BaseCaster, PLACEHOLDER


class IterableCaster[TType](BaseCaster[bytes, TType]):
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
    def to_database(self) -> bytes:
        return tuple(self.value)

    @property
    def from_database(self) -> bytes:
        return tuple(self.value)

    @property
    def string_data(self) -> str:
        return str(self.value)
