from __future__ import annotations
from typing import Callable, Optional, Type, TYPE_CHECKING
from ormlambda import util
import importlib

if TYPE_CHECKING:
    from .interface import Dialect


__all__ = ("mysql", "sqlite")


def _auto_fn(name: str) -> Optional[Callable[[], Type[Dialect]]]:
    """default dialect importer.

    plugs into the :class:`.PluginLoader`
    as a first-hit system.

    """
    if "." in name:
        dialect, driver = name.split(".")
    else:
        dialect = name
        driver = "base"

    try:
        module = importlib.import_module(f"ormlambda.dialects.{dialect}")

    except ImportError:
        return None

    if hasattr(module, driver):
        module = getattr(module, driver)
        return lambda: module.dialect
    else:
        return None


registry = util.PluginLoader("ormlambda.dialects", auto_fn=_auto_fn)
