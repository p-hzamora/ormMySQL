from typing import Optional, Any, TypeGuard, Iterable
import collections.abc as collections_abc


def is_non_string_iterable(obj: Any) -> TypeGuard[Iterable[Any]]:
    return isinstance(obj, collections_abc.Iterable) and not isinstance(obj, (str, bytes))


def to_list(x: Any, default: Optional[list[Any]] = None) -> list[Any]:
    if x is None:
        return default  # type: ignore
    if not is_non_string_iterable(x):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return list(x)
