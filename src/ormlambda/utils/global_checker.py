from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ormlambda.common.errors import UnmatchedLambdaParameterError

if TYPE_CHECKING:
    from ormlambda import Table


class GlobalChecker:
    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)

    @classmethod
    def resolved_callback_object(cls, obj: Any, tables: tuple[Table, ...]):
        if not cls.is_lambda_function(obj):
            return obj

        try:
            return obj(*tables)
        except TypeError:
            raise UnmatchedLambdaParameterError(len(tables), obj)
