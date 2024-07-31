# Standard libraries
from functools import wraps
from pathlib import Path
from typing import Any, Literal, Type, override


from mysql.connector import Error, MySQLConnection, errorcode

# Custom libraries
from orm.common.interfaces import IRepositoryBase
from orm.utils import Table, Column, ForeignKey
from orm.utils.module_tree.dynamic_module import ModuleTree
from orm.utils.dtypes import get_query_clausule

type_exists = Literal["fail", "replace", "append"]


class Response[TFlavour, *Ts]:
    def __init__(self, response_values: list[tuple[*Ts]], columns: tuple[str], flavour: Type[TFlavour], **kwargs) -> None:
        self._response_values: list[tuple[*Ts]] = response_values
        self._columns: tuple[str] = columns
        self._flavour: Type[TFlavour] = flavour
        self._kwargs: dict[str, Any] = kwargs

        self._response_values_index: int = len(self._response_values)
        # self.select_values()

    @property
    def is_one(self) -> bool:
        return self._response_values_index == 1

    @property
    def is_there_response(self) -> bool:
        return self._response_values_index != 0

    @property
    def is_many(self) -> bool:
        return self._response_values_index > 1

    @property
    def response(self) -> tuple[dict[str, tuple[*Ts]]] | tuple[tuple[*Ts]] | tuple[TFlavour]:
        if not self.is_there_response:
            return tuple([])

        return tuple(self._cast_to_flavour(self._response_values))

    def _cast_to_flavour(self, data: list[tuple[*Ts]]) -> list[dict[str, tuple[*Ts]]] | list[tuple[*Ts]] | list[TFlavour]:
        def _dict() -> list[dict[str, tuple[*Ts]]]:
            return [dict(zip(self._columns, x)) for x in data]

        def _tuple() -> list[tuple[*Ts]]:
            return data

        def _default() -> list[TFlavour]:
            return [self._flavour(x, **self._kwargs) for x in data]

        selector: dict[Type[object], Any] = {dict: _dict, tuple: _tuple}

        return selector.get(self._flavour, _default)()


class MySQLRepository(MySQLConnection, IRepositoryBase[MySQLConnection]):
    @staticmethod
    def _is_connected(func):
        @wraps(func)
        def wrapper(self: "MySQLRepository", *args, **kwargs):
            if not self.is_connected():
                self.connect()

            foo = func(self, *args, **kwargs)
            self.close()
            return foo

        return wrapper

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _close_connection(self) -> None:
        if self.is_connected():
            self.close()
        return None

    @_is_connected
    def read_sql[TFlavour](self, query: str, flavour: Type[TFlavour] = tuple, **kwargs) -> tuple[TFlavour]:
        """ """

        with self.cursor(buffered=True) as cursor:
            cursor.execute(query)
            values: list[tuple] = cursor.fetchall()
            columns: tuple[str] = cursor.column_names
            return Response[TFlavour](response_values=values, columns=columns, flavour=flavour, **kwargs).response

    # FIXME [ ]: this method does not comply with the implemented interface
    @_is_connected
    def create_tables_code_first(self, path: str | Path) -> None:
        def create_sql_column_query(table_object: Table) -> list[str]:
            annotations: dict[str, Column] = table_object.__annotations__
            all_columns: list = []
            for col_name in annotations.keys():
                col_object: Column = getattr(table_object, f"_{col_name}")
                all_columns.append(get_query_clausule(col_object))
            return all_columns

        if not isinstance(path, Path | str):
            raise ValueError

        if isinstance(path, str):
            path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError

        module_tree: ModuleTree = ModuleTree(path)

        table_objects: tuple[Type[Table]] = module_tree.get_tables()

        queries_list: list[str] = []
        for table_object in table_objects:
            table_init = table_object()
            all_clauses: list[str] = []

            all_clauses.extend(create_sql_column_query(table_init))
            all_clauses.extend(ForeignKey.create_query(table_object))

            queries_list.append(f"CREATE TABLE {table_init.__table_name__} ({', '.join(all_clauses)});")

        for query in queries_list:
            with self.cursor(buffered=True) as cursor:
                cursor.execute(query)
                self.commit()
        return None

    @override
    @_is_connected
    def executemany_with_values(self, query: str, values) -> None:
        with self.cursor(buffered=True) as cursor:
            cursor.executemany(query, values)
            self.commit()
        return None

    @override
    @_is_connected
    def execute_with_values(self, query: str, values) -> None:
        with self.cursor(buffered=True) as cursor:
            cursor.execute(query, values)
            self.commit()
        return None

    @override
    @property
    def connection(self) -> MySQLConnection:
        return self
