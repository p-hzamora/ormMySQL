from __future__ import annotations
import re
from typing import Any, TYPE_CHECKING, Iterable, Type, Callable

from ormlambda.common.errors import UnmatchedLambdaParameterError

if TYPE_CHECKING:
    from ormlambda.sql.context import PathContext
    from ormlambda.sql import Table
    from ormlambda.sql.table import TableProxy
    from ormlambda.sql.column import ColumnProxy


class GlobalChecker:
    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)

    @classmethod
    def resolved_callback_object(cls, lambda_func: Callable[[Type[Table]], Any], table: Type[Table], context: PathContext) -> tuple[ColumnProxy | TableProxy, ...]:
        from ormlambda.sql.table import TableProxy
        from ormlambda import Column
        from ormlambda.sql.column_table_proxy import FKChain
        from ormlambda.sql.column import ColumnProxy

        try:
            table_proxy = TableProxy(table, context.get_current_path())
            response = lambda_func(table_proxy)
            result = []


            if isinstance(response, str) or not isinstance(response, Iterable):
                response = [response]

            for item in response:
                if isinstance(item, TableProxy):
                    result.extend(item.get_columns())

                if isinstance(item, str):
                    new_col = Column(dtype=str, column_name=item)
                    new_col.table = table
                    result = ColumnProxy(new_col, path=FKChain(table, None))
                else:
                    result.append(item)

            return result

        except TypeError as err:
            cond1 = r"takes \d+ positional argument but \d+ were given"
            cond2 = r"missing \d+ required positional arguments:"
            if re.search(r"(" + f"{cond1}|{cond2}" + r")", err.args[0]):
                raise UnmatchedLambdaParameterError(len(table), lambda_func)
            raise err
