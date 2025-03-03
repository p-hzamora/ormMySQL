from ormlambda.caster import BaseCaster, PLACEHOLDER


class StringCaster[TType](BaseCaster[str, TType]):
    def __init__(self, value: str, type_value: TType):
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
    def to_database(self) -> str:
        return str(self.value)

    @property
    def from_database(self) -> str:
        return str(self.value)
