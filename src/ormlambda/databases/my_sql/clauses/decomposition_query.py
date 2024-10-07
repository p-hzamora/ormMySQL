import typing as tp

from ormlambda import Table

from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction
from ormlambda.common.interfaces import IAggregate
from ormlambda.components.select.table_column import TableColumn


class DecompositionQuery[T: tp.Type[Table]]:
    @tp.overload
    def __init__(self, table: T, query: str, alias: bool = True) -> None: ...
    @tp.overload
    def __init__[*Ts](self, table: T, query: tp.Callable[[T], tuple[*Ts]], alias: bool = True) -> None: ...

    def __init__[*Ts](self, table: T, query: str | tp.Callable[[T], tuple[*Ts]], alias: bool = True) -> None:
        self._table: T = table
        self._callback: str | tp.Callable[[T], tuple[Ts]] = query
        self._alias: bool = alias

    def create_list[*Ts](self, query: tuple[*Ts]) -> list[str]:
        tree_list = TreeInstruction(self._callback).to_list()
        result: list[str] = []

        for index, value in enumerate(query):
            # if property is attached to self._table, we create string
            if isinstance(value, property) and value in self._table.__properties_mapped__:
                table: str = self._table.__table_name__
                name: str = self._table.__properties_mapped__[value]
                value = f"{table}.{name}{f" as `{table}_{name}`" if self._alias else ""}"

            elif isinstance(value, property) and value not in self._table.__properties_mapped__:
                temp_table: tp.Type[Table] = self._table

                table_list: list[Table] = tree_list[index].nested_element.parents[1:]
                counter: int = 0
                while value not in temp_table.__properties_mapped__:
                    new_table: tp.Type[Table] = getattr(temp_table(), table_list[counter])
                    temp_table = new_table
                    counter += 1

                    if value in new_table.__properties_mapped__:
                        table: str = new_table.__table_name__
                        name: str = new_table.__properties_mapped__[value]

                        value = f"{table}.{name}{f" as `{table}_{name}`" if self._alias else ""}"
                        break

            elif isinstance(value, IAggregate):
                value = value.query

            elif issubclass(value, Table):
                # all columns
                value = ", ".join([x.column for x in TableColumn.all_columns(value)])

            else:
                raise NotImplementedError

            result.append(value)
        return result

    @property
    def query(self) -> str:
        if isinstance(self._callback, str):
            return self._callback

        return self._build(self._callback)

    def _build[*Ts](self, callback: str | tp.Callable[[T], tuple[*Ts]]) -> str:
        resolved_func = callback(self._table)

        if isinstance(resolved_func, tp.Iterable):
            result = self.create_list(resolved_func)

        elif isinstance(resolved_func, property):
            result = self.create_list([resolved_func])
        else:
            raise NotImplementedError

        return ", ".join(result)
