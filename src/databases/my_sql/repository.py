# Standard libraries
from pathlib import Path
from typing import Any, Type, override


# from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import MySQLConnection, Error  # noqa: F401

# Custom libraries
from ...common.interfaces import IRepositoryBase
from ...utils.module_tree.dynamic_module import ModuleTree

from .clauses import CreateDatabase, TypeExists
from .clauses import DropDatabase
from .clauses import DropTable


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


class MySQLRepository(IRepositoryBase[MySQLConnection]):
    def __init__(self, **kwargs: Any) -> None:
        self._data_config: dict[str, Any] = kwargs
        self._connection: MySQLConnection = MySQLConnection()
        # self._pool_connection: MySQLConnection = MySQLConnection(**kwargs)
        pass

    @override
    def is_connected(self) -> bool:
        return self._connection.is_connected()

    @override
    def connect(self) -> IRepositoryBase[MySQLConnection]:
        # return MySQLConnectionPool(pool_name="mypool", pool_size=5, **kwargs)
        self._connection.connect(**self._data_config)
        return None

    @override
    def close_connection(self) -> None:
        if self._connection.is_connected():
            self._connection.close()
        return None

    @override
    @IRepositoryBase.check_connection
    def read_sql[TFlavour](self, query: str, flavour: Type[TFlavour] = tuple, **kwargs) -> tuple[TFlavour]:
        """
        Return tuple of tuples by default.

        ATTRIBUTE
        -
            - query:str: string of request to the server
            - flavour: Type[TFlavour]: Useful to return tuple of any Iterable type as dict,set,list...
        """

        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            values: list[tuple] = cursor.fetchall()
            columns: tuple[str] = cursor.column_names
            return Response[TFlavour](response_values=values, columns=columns, flavour=flavour, **kwargs).response

    # FIXME [ ]: this method does not comply with the implemented interface
    @IRepositoryBase.check_connection
    def create_tables_code_first(self, path: str | Path) -> None:
        if not isinstance(path, Path | str):
            raise ValueError

        if isinstance(path, str):
            path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError

        module_tree: ModuleTree = ModuleTree(path)

        queries_list: list[str] = module_tree.get_queries()

        for query in queries_list:
            with self._connection.cursor(buffered=True) as cursor:
                cursor.execute(query)
        self._connection.commit()
        return None

    @override
    @IRepositoryBase.check_connection
    def executemany_with_values(self, query: str, values) -> None:
        with self._connection.cursor(buffered=True) as cursor:
            cursor.executemany(query, values)
        self._connection.commit()
        return None

    @override
    @IRepositoryBase.check_connection
    def execute_with_values(self, query: str, values) -> None:
        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query, values)
        self._connection.commit()
        return None

    @override
    @IRepositoryBase.check_connection
    def execute(self, query: str) -> None:
        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
        self._connection.commit()
        return None

    @override
    @IRepositoryBase.check_connection
    def drop_table(self, name: str) -> None:
        return DropTable(self).execute(name)

    @override
    @IRepositoryBase.check_connection
    def database_exists(self, name: str) -> bool:
        query = "SHOW DATABASES LIKE %s;"
        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @override
    @IRepositoryBase.check_connection
    def drop_database(self, name: str) -> None:
        return DropDatabase(self).execute(name)

    @override
    @IRepositoryBase.check_connection
    def table_exists(self, name: str) -> bool:
        if not self._connection.database:
            raise Exception("No database selected")

        query = "SHOW TABLES LIKE %s;"
        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @override
    @IRepositoryBase.check_connection
    def create_database(self, name: str, if_exists: TypeExists = "fail") -> None:
        return CreateDatabase(self).execute(name, if_exists)

    @override
    @property
    def connection(self) -> MySQLConnection:
        return self._connection

    @override
    def set_config(self, value: dict[str, Any]) -> dict[str, Any]:
        return self._data_config.update(value)
