import types
import inspect
from typing import Literal, Optional, overload, Callable
from types import ModuleType
from ormlambda import errors


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


class PluginLoader:
    def __init__(self, group: str, auto_fn: Optional[Callable[..., ModuleType]] = None):
        self.group = group
        self.impls: dict[str, ModuleType] = {}
        self.auto_fn = auto_fn

    def clear(self):
        self.impls.clear()

    def load(self, name: str) -> Optional[ModuleType]:
        if name in self.impls:
            return self.impls[name]()
        if self.auto_fn:
            loader = self.auto_fn(name)
            if loader:
                self.impls[name] = loader
                return loader()
        raise errors.NoSuchModuleError(f"Can't load plugin: {self.group}:{name}")

    def register(self, name: str, modulepath: str, objname: str) -> None:
        def load():
            mod = __import__(modulepath)
            for token in modulepath.split(".")[1:]:
                mod = getattr(mod, token)
            return getattr(mod, objname)

        self.impls[name] = load
