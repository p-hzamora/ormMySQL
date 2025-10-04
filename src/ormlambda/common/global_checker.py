from __future__ import annotations
import re
from typing import Any, TYPE_CHECKING, Iterable, Type, Callable

from ormlambda.common.errors import UnmatchedLambdaParameterError

if TYPE_CHECKING:
    from ormlambda.sql.types import SelectCol  # FIXME [ ]: enhance the name
    from ormlambda import TableProxy


# type LambdaResponse[T] = TableProxy[T] | ColumnProxy[T] | Comparer
class GlobalChecker:
    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)

    @classmethod
    def resolved_callback_object(cls, table: T, lambda_func: Callable[[T], Any]) -> tuple[SelectCol, ...]:

        try:
            table_proxy = TableProxy(table, FKChain(table, []))

            if not callable(lambda_func) and isinstance(lambda_func, Iterable):
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
                if isinstance(item, TableProxy):
                    result.extend(item.get_columns())

                elif isinstance(item, str):
                    # If we got a string, probably means that it'll be an alias,
                    # so we'll want to avoid add string alias table to alias like  `address`.count
                    new_col = Column(dtype=str, column_name=item)
                    new_col.table = table
                    result.append(ColumnProxy(new_col, path=FKChain(table, None)))
                elif isinstance(item, Comparer):
                    result.append(item)

                elif isinstance(item, ColumnProxy):
                    result.append(item)

                else:
                    result.append(item)

            return result

        except TypeError as err:
            cond1 = r"takes \d+ positional argument but \d+ were given"
            cond2 = r"missing \d+ required positional arguments:"
            if re.search(r"(" + f"{cond1}|{cond2}" + r")", err.args[0]):
                raise UnmatchedLambdaParameterError(len(table), lambda_func)
            raise err
