from .module_tree import ModuleTree  # noqa: F401
from .load_module import __load_module__  # noqa: F401
import types
import inspect
from typing import Any, Literal, Optional, Sequence, overload, get_origin, TypeGuard, TypeAliasType
from ormlambda.util.typing import LITERAL_TYPES, _AnnotationScanType
from .plugin_loader import PluginLoader  # noqa: F401


def _inspect_func_args(fn) -> tuple[list[str], bool]:
    try:
        co_varkeywords = inspect.CO_VARKEYWORDS
    except AttributeError:
        # https://docs.python.org/3/library/inspect.html
        # The flags are specific to CPython, and may not be defined in other
        # Python implementations. Furthermore, the flags are an implementation
        # detail, and can be removed or deprecated in future Python releases.
        spec = inspect.getfullargspec(fn)
        return spec[0], bool(spec[2])
    else:
        # use fn.__code__ plus flags to reduce method call overhead
        co = fn.__code__
        nargs = co.co_argcount
        return (
            list(co.co_varnames[:nargs]),
            bool(co.co_flags & co_varkeywords),
        )


@overload
def get_cls_kwargs(cls: type, *, _set: Optional[set[str]] = None, raiseerr: Literal[True] = ...) -> set[str]: ...


@overload
def get_cls_kwargs(cls: type, *, _set: Optional[set[str]] = None, raiseerr: Literal[False] = ...) -> Optional[set[str]]: ...


def get_cls_kwargs(cls: type, *, _set: Optional[set[str]] = None, raiseerr: bool = False) -> Optional[set[str]]:
    """
    Get the keyword arguments for a class constructor.
    Args:
        cls: The class to inspect.
        _set: A set to store the keyword arguments.
        raiseerr: Whether to raise an error if the class is not found.
    Returns:
        A set of keyword arguments for the class constructor.
    """
    toplevel = _set is None
    if toplevel:
        _set = set()
    assert _set is not None

    ctr = cls.__dict__.get("__init__", False)

    has_init = ctr and isinstance(ctr, types.FunctionType) and isinstance(ctr.__code__, types.CodeType)

    if has_init:
        names, has_kw = _inspect_func_args(ctr)
        _set.update(names)

        if not has_kw and not toplevel:
            if raiseerr:
                raise TypeError(f"given cls {cls} doesn't have an __init__ method")
            else:
                return None
    else:
        has_kw = False

    if not has_init or has_kw:
        for c in cls.__bases__:
            if get_cls_kwargs(c, _set=_set) is None:
                break

    _set.discard("self")
    return _set


def avoid_sql_injection(name: str):
    if any(char in name for char in [";", "--", "/*", "*/"]):
        raise ValueError("SQL injection detected")


def is_literal(type_: Any) -> bool:
    return get_origin(type) in LITERAL_TYPES


def is_pep695(type_: _AnnotationScanType) -> TypeGuard[TypeAliasType]:
    return isinstance(type_, TypeAliasType)
