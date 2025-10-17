from __future__ import annotations
from typing import Type, Union, get_origin, get_args, TYPE_CHECKING
from .preloaded import preload_module as preload_module
from .preloaded import import_prefix as import_prefix
import inspect
from . import preloaded as preloaded

from .langhelpers import get_cls_kwargs as get_cls_kwargs
from .langhelpers import PluginLoader as PluginLoader

from .typing import is_literal as is_literal
from .typing import is_pep695 as is_pep695

if TYPE_CHECKING:
    from ormlambda.sql.type_api import TypeEngine


def is_optional(type_: Type) -> bool:
    if get_origin(type_) is not Union:
        return False

    args = get_args(type_)

    return len(args) == 2 and type(None) in args


@preload_module(
    "ormlambda.sql.column",
    "ormlambda.sql.sqltypes",
)
def get_type[TProp](type_: TProp, recursive: bool = True) -> TypeEngine:
    Column = preloaded.sql_column.Column
    TypeEngine = preloaded.sql_sqltypes.TypeEngine

    if inspect.isclass(type_) and issubclass(type_, TypeEngine):
        return type_()

    if isinstance(type_, TypeEngine):
        return type_

    if get_origin(type_) is Column:
        # We can assume that if type_ is Column, should have one args because always should be `data:Column[some_type]`
        args = get_args(type_)[0]

        return get_type(args, recursive=False)

    if recursive and (args := get_args(type_)):
        return get_type(args[0])

    return TypeEngine().coerce_compared_value(type_)
