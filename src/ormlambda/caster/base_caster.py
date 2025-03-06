from typing import Type, Callable, Optional
import abc


class BaseCaster[TProp, TType](abc.ABC):
    def __init__(self, value: TProp, type_value: TType):
        self._value: TProp = value
        self._type_value: TType = type_value

    def __repr__(self):
        return f"{BaseCaster.__name__}: [{type(self._value).__name__}] -> [{self.type_to_cast.__name__}]"

    @property
    @abc.abstractmethod
    def wildcard_to_select(self) -> str: ...

    @property
    @abc.abstractmethod
    def wildcard_to_where(self) -> str: ...

    @property
    @abc.abstractmethod
    def wildcard_to_insert(self) -> str: ...

    @property
    @abc.abstractmethod
    def to_database(self) -> Type[TProp]: ...

    @property
    @abc.abstractmethod
    def from_database(self) -> TProp: ...

    @property
    @abc.abstractmethod
    def string_data(self) -> str: ...

    @property
    def value(self) -> TProp:
        return self._value

    @property
    def value_type(self) -> Type[TProp]:
        return type(self._value)

    @property
    def type_to_cast(self) -> TType:
        return self._type_value

    @staticmethod
    def return_value_if_exists[TType, **P](func: Callable[P, Optional[TType]]) -> Callable[P, Optional[TType]]:
        def wrapped(self:"BaseCaster") -> Optional[TType]:
            if self._value is None:
                return None

            return func(self)

        return wrapped
