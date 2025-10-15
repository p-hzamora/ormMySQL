from __future__ import annotations
from typing import Any, Type, Iterable, Literal, TYPE_CHECKING
from collections import defaultdict


from ormlambda import Table

from ormlambda.common.errors import FunctionFunctionError
from ormlambda import util


if TYPE_CHECKING:
    from ormlambda.engine.base import Engine
    from ormlambda.sql.clauses import Select
    from ormlambda import ColumnProxy


ORDER_QUERIES = Literal["select", "join", "where", "order", "with", "group by", "limit", "offset"]


type ResponseType = Iterable[dict[str, Any]]


class ClusterResponse[T, TFlavour]:
    def __init__(self, select: Select[T], engine: Engine, flavour: TFlavour, query: str) -> None:
        self._select: Select[T] = select
        self.engine = engine
        self.flavour = flavour
        self.query = query

    @util.preload_module("ormlambda.sql.functions")
    def cluster(self, response_sql: ResponseType) -> tuple[dict[Type[Table], tuple[Table, ...]]]:
        # We'll create a default list of dicts *once* we know how many rows are in _response_sql

        IFunction = util.preloaded.sql_functions.IFunction

        tables: dict[Table, Iterable[ColumnProxy]] = defaultdict(list)
        for clause in self._select.columns:
            if isinstance(clause, IFunction):
                raise FunctionFunctionError(clause)

            tables[clause.table].append(clause)

        res = []
        for dicc_cols in response_sql:
            converted_row = []
            for table, columns in tables.items():
                dicc = {}
                for col in columns:
                    if not hasattr(col, "column_name"):
                        pass
                    dicc[col.column_name] = dicc_cols[col.alias]
                converted_row.append(table(**dicc))
            res.append(tuple(converted_row))

        tuple_response = tuple(res)

        if not tuple_response:
            return tuple_response

        if len(tuple_response) == 1:
            return tuple_response[0]

        if len(tuple_response[0]) == 1:
            return tuple([x[0] for x in tuple_response])
        return tuple_response

    def cluster_data(self, **kwargs) -> TFlavour[T, ...]:
        if not self.flavour:
            return self._return_model()

        return self._return_flavour(self.flavour, **kwargs)

    def _return_flavour[TValue](self, flavour: Type[TValue], **kwargs) -> tuple[TValue]:
        return self.engine.repository.read_sql(
            query=self.query,
            flavour=flavour,
            select=self._select,
            **kwargs,
        )

    def _return_model(self) -> tuple[tuple[T]]:
        response_sql = self._return_flavour(flavour=dict)

        if response_sql and isinstance(response_sql, Iterable):
            return self.cluster(response_sql)

        return response_sql
