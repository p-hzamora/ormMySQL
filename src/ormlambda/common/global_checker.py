from __future__ import annotations
import re
from typing import Any, TYPE_CHECKING, Type

from ormlambda.common.errors import UnmatchedLambdaParameterError

if TYPE_CHECKING:
    from ormlambda.sql import Table
    from ormlambda.sql.column import ColumnProxy
    from ormlambda.sql.table import TableProxy


class GlobalChecker:
    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)

    @classmethod
    def resolved_callback_object(cls, obj: Any, table: Type[Table|TableProxy]) -> tuple[ColumnProxy | TableProxy, ...]:
        from ormlambda.sql.context import PATH_CONTEXT
        from ormlambda.sql.table import TableProxy

        if isinstance(table,TableProxy):
            table = table._table_class

        if not cls.is_lambda_function(obj):
            return obj
            raise ValueError

        try:
            with PATH_CONTEXT.query_context(table) as context:
                table_proxy = TableProxy(table, context.get_current_path())
                return obj(table_proxy)
        except TypeError as err:
            cond1 = r"takes \d+ positional argument but \d+ were given"
            cond2 = r"missing \d+ required positional arguments:"
            if re.search(r"(" + f"{cond1}|{cond2}" + r")", err.args[0]):
                raise UnmatchedLambdaParameterError(len(table), obj)
            raise err
