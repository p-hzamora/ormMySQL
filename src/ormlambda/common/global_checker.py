from __future__ import annotations
import re
from typing import Any, TYPE_CHECKING

from ormlambda.common.errors import UnmatchedLambdaParameterError

if TYPE_CHECKING:
    from ormlambda.sql import Table


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
        except TypeError as err:
            if re.search(r"takes \d+ positional argument but \d+ were given", err.args[0]):
                raise UnmatchedLambdaParameterError(len(tables), obj)
            raise err
