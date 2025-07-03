from __future__ import annotations
from typing import Any, ClassVar
from ormlambda.sql.visitors import Element
import abc


class TypeEngine[T: Any](Element, abc.ABC):
    """
    Base class for all SQL types.
    """

    __visit_name__ = "type_engine"

    _sqla_type: ClassVar[bool] = True
    _isnull: ClassVar[bool] = False
    _is_tuple_type: ClassVar[bool] = False
    _is_table_value: ClassVar[bool] = False
    _is_array: ClassVar[bool] = False
    _is_type_decorator: ClassVar[bool] = False
    _type: ClassVar[T]

    @property
    @abc.abstractmethod
    def python_type(self) -> T: ...

    def _resolve_for_literal_value(self, value: T) -> TypeEngine[T]:
        return self

    def coerce_compared_value[TType](self, value: TType) -> TypeEngine[TType]:
        from .sqltypes import resolve_primitive_types, NULLTYPE

        _coerced_type = resolve_primitive_types(value)
        if _coerced_type is NULLTYPE:
            return self
        return _coerced_type

    def __repr__(self):
        return f"{TypeEngine.__name__}: {super().__repr__()}"
