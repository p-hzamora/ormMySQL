from __future__ import annotations
from typing import Type, Any, TYPE_CHECKING, Optional
from ormlambda.dialects.interface.dialect import Dialect
import shapely as shp

# Custom libraries
from ormlambda.sql.clauses import Alias

if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo
    from ormlambda import Table
    from ormlambda.sql.clauses import Select


type TResponse[TFlavour, *Ts] = TFlavour | tuple[dict[str, tuple[*Ts]]] | tuple[tuple[*Ts]] | tuple[TFlavour]


class Response[TFlavour, *Ts]:
    def __init__(
        self,
        dialect: Dialect,
        response_values: list[tuple[*Ts]],
        columns: tuple[str],
        flavour: Type[TFlavour],
        select: Optional[Select] = None,
    ) -> None:
        self._dialect: Dialect = dialect
        self._response_values: list[tuple[*Ts]] = response_values
        self._columns: tuple[str] = columns
        self._flavour: Type[TFlavour] = flavour
        self._select: Select = select

        self._response_values_index: int = len(self._response_values)

        self._caster = dialect.caster()

    @property
    def is_one(self) -> bool:
        return self._response_values_index == 1

    @property
    def is_there_response(self) -> bool:
        return self._response_values_index != 0

    @property
    def is_many(self) -> bool:
        return self._response_values_index > 1

    def response(self, **kwargs) -> TResponse[TFlavour, *Ts]:
        if not self.is_there_response:
            return tuple([])

        # Cast data using caster
        cleaned_response = self._response_values

        if self._select is not None:
            cleaned_response = self._clean_response()

        cast_flavour = self._cast_to_flavour(cleaned_response, **kwargs)

        return tuple(cast_flavour)

    def _cast_to_flavour(self, data: list[tuple[*Ts]], **kwargs) -> list[dict[str, tuple[*Ts]]] | list[tuple[*Ts]] | list[TFlavour]:
        def _dict(**kwargs) -> list[dict[str, tuple[*Ts]]]:
            nonlocal data
            return [dict(zip(self._columns, x)) for x in data]

        def _tuple(**kwargs) -> list[tuple[*Ts]]:
            nonlocal data
            return data

        def _set(**kwargs) -> list[set]:
            nonlocal data
            for d in data:
                n = len(d)
                for i in range(n):
                    try:
                        hash(d[i])
                    except TypeError:
                        raise TypeError(f"unhashable type '{type(d[i])}' found in '{type(d)}' when attempting to cast the result into a '{set.__name__}' object")
            return [set(x) for x in data]

        def _list(**kwargs) -> list[list]:
            nonlocal data
            return [list(x) for x in data]

        def _default(**kwargs) -> list[TFlavour]:
            nonlocal data
            replacer_dicc: dict[str, str] = {}

            for col in self._select.all_clauses:
                if hasattr(col, "_alias_aggregate") or col.alias_clause is None or isinstance(col, Alias):
                    continue
                replacer_dicc[col.alias_clause] = col.column

            cleaned_column_names = [replacer_dicc.get(col, col) for col in self._columns]

            result = []
            for attr in data:
                dicc_attr = dict(zip(cleaned_column_names, attr))
                result.append(self._flavour(**dicc_attr, **kwargs))

            return result

        selector: dict[Type[object], Any] = {
            dict: _dict,
            tuple: _tuple,
            set: _set,
            list: _list,
        }
        return selector.get(self._flavour, _default)(**kwargs)

    def _clean_response(self) -> TFlavour:
        new_response: list[tuple] = []
        for row in self._response_values:
            new_row: list = []
            for i, data in enumerate(row):
                alias = self._columns[i]
                clause_info = self._select[alias]
                parse_data = self._caster.for_value(data, value_type=clause_info.dtype).from_database
                new_row.append(parse_data)
            new_row = tuple(new_row)
            if not isinstance(new_row, tuple):
                new_row = tuple(new_row)

            new_response.append(new_row)
        return new_response

    @staticmethod
    def _is_parser_required[T: Table](clause_info: ClauseInfo[T]) -> bool:
        if clause_info is None:
            return False

        return clause_info.dtype is shp.Point
