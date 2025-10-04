import typing_extensions as tpe
from typing import Any, Literal, Type, NewType, get_origin, TypeGuard, TypeAliasType


LITERAL_TYPES = frozenset([Literal, tpe.Literal])

type _AnnotationScanType = Type[Any] | str | NewType


def is_literal(type_: Any) -> bool:
    return get_origin(type) in LITERAL_TYPES


def is_pep695(type_: _AnnotationScanType) -> TypeGuard[TypeAliasType]:
    return isinstance(type_, TypeAliasType)
