from __future__ import annotations
import re
from typing import Any, TYPE_CHECKING, Iterable, Callable

from ormlambda.common.errors import UnmatchedLambdaParameterError
from ormlambda.common.errors import NotCallableError
from ormlambda import util

if TYPE_CHECKING:
    from ormlambda.sql.types import SelectCol  # FIXME [ ]: enhance the name
    from ormlambda import TableProxy
    from ormlambda.sql.column import ColumnProxy


# type LambdaResponse[T] = TableProxy[T] | ColumnProxy[T] | Comparer
class GlobalChecker[T: TableProxy]:
    FIRST_QUOTE = "`"
    END_QUOTE = "`"

    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)

    @util.preload_module("ormlambda.sql")
    @classmethod
    def resolved_callback_object(cls, table: T, lambda_func: Callable[[T], Any]) -> tuple[SelectCol, ...]:
        TableProxy = util.preloaded.sql_table.TableProxy

        try:
            table_proxy = TableProxy(table)

            if not callable(lambda_func): 
                raise NotCallableError(lambda_func)

            if isinstance(lambda_func, Iterable):
                # We hit that condition when trying to pass column or function dynamically into select clause.

                # max_fn = Max(lambda x: x.Col1)
                # min_fn = Min(lambda x: x.Col1)
                # sum_fn = Sum(lambda x: x.Col1)
                # result = self.model.select(
                #     (
                #         max_fn,
                #         min_fn,
                #         sum_fn,
                #     ),
                #     flavour=dict,
                # )

                response = []

                for item in lambda_func:
                    response.append(item)
                return response

            response = lambda_func(table_proxy)
            result = []

            if isinstance(response, str) or not isinstance(response, Iterable):
                response = [response]

            for item in response:
                column = cls.parser_object(item, table)

                result.extend(column)

            return result

        except TypeError as err:
            cond1 = r"takes \d+ positional argument but \d+ were given"
            cond2 = r"missing \d+ required positional arguments:"
            if re.search(r"(" + f"{cond1}|{cond2}" + r")", err.args[0]):
                raise UnmatchedLambdaParameterError(len(table), lambda_func)
            raise err

    @util.preload_module(
        "ormlambda.sql.column",
        "ormlambda.sql.table",
        "ormlambda.sql.comparer",
        "ormlambda.sql.column_table_proxy",
    )
    @staticmethod
    def parser_object(item: Any, table: T) -> tuple[ColumnProxy, ...]:
        ColumnProxy = util.preloaded.sql_column.ColumnProxy
        Column = util.preloaded.sql_column.Column

        TableProxy = util.preloaded.sql_table.TableProxy
        Comparer = util.preloaded.sql_comparer.Comparer
        FKChain = util.preloaded.sql_column_table_proxy.FKChain

        if isinstance(item, TableProxy):
            return item.get_columns()

        if isinstance(item, str):
            # If we got a string, probably means that it'll be an alias,
            # so we'll want to avoid add string alias table to alias like  `address`.count
            new_col = Column(dtype=str, column_name=item)
            new_col.table = table
            return [ColumnProxy(new_col, path=FKChain(table, None))]
        if isinstance(item, Comparer):
            return [item]

        if isinstance(item, ColumnProxy):
            return [item]

        return [item]
