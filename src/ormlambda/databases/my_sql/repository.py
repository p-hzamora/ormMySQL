from __future__ import annotations
from pathlib import Path
from typing import Any, Optional, Type, override, Callable, TYPE_CHECKING
import functools
import shapely as shp

# from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import MySQLConnection, Error  # noqa: F401
from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionPool  # noqa: F401

# Custom libraries
from ormlambda import IRepositoryBase
from ormlambda.utils.module_tree.dynamic_module import ModuleTree

from .clauses import CreateDatabase, TypeExists
from .clauses import DropDatabase
from .clauses import DropTable


if TYPE_CHECKING:
    from src.ormlambda.common.abstract_classes.decomposition_query import ClauseInfo
    from ormlambda import Table
    from src.ormlambda.databases.my_sql.clauses.select import Select

type TResponse[TFlavour, *Ts] = TFlavour | tuple[dict[str, tuple[*Ts]]] | tuple[tuple[*Ts]] | tuple[TFlavour]


class Response[TFlavour, *Ts]:
    def __init__(self, response_values: list[tuple[*Ts]], columns: tuple[str], flavour: Type[TFlavour], model: Optional[Table] = None, select: Optional[Select] = None) -> None:
        self._response_values: list[tuple[*Ts]] = response_values
        self._columns: tuple[str] = columns
        self._flavour: Type[TFlavour] = flavour
        self._model: Table = model
        self._select: Select = select

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

    def response(self, _tuple: bool, **kwargs) -> TResponse[TFlavour, *Ts]:
        if not self.is_there_response:
            return tuple([])
        cleaned_response = self._response_values

        if self._select is not None:
            cleaned_response = self._parser_response()

        cast_flavour = self._cast_to_flavour(cleaned_response, **kwargs)
        if _tuple is not True:
            return cast_flavour

        return tuple(cast_flavour)

    def _cast_to_flavour(self, data: list[tuple[*Ts]], **kwargs) -> list[dict[str, tuple[*Ts]]] | list[tuple[*Ts]] | list[TFlavour]:
        def _dict(**kwargs) -> list[dict[str, tuple[*Ts]]]:
            return [dict(zip(self._columns, x)) for x in data]

        def _tuple(**kwargs) -> list[tuple[*Ts]]:
            return data

        def _set(**kwargs) -> list[set]:
            for d in data:
                n = len(d)
                for i in range(n):
                    try:
                        hash(d[i])
                    except TypeError:
                        raise TypeError(f"unhashable type '{type(d[i])}' found in '{type(d)}' when attempting to cast the result into a '{set.__name__}' object")
            return [set(x) for x in data]

        def _list(**kwargs) -> list[list]:
            return [list(x) for x in data]

        def _default(**kwargs) -> list[TFlavour]:
            return self._flavour(data, **kwargs)

        selector: dict[Type[object], Any] = {
            dict: _dict,
            tuple: _tuple,
            set: _set,
            list: _list,
        }

        return selector.get(self._flavour, _default)(**kwargs)

    def _parser_response(self) -> TFlavour:
        new_response: list[list] = []
        for row in self._response_values:
            new_row: list = []
            for i, data in enumerate(row):
                alias = self._columns[i]
                clause_info = self._select[alias]
                if not self._is_parser_required(clause_info):
                    new_row = row
                    break
                else:
                    parser_data = self.parser_data(clause_info, data)
                    new_row.append(parser_data)
            if not isinstance(new_row, tuple):
                new_row = tuple(new_row)

            new_response.append(new_row)
        return new_response

    @staticmethod
    def _is_parser_required[T: Table](clause_info: ClauseInfo[T]) -> bool:
        if clause_info is None:
            return False

        return clause_info.dtype is shp.Point

    @staticmethod
    def parser_data[T: Table, TProp](clause_info: ClauseInfo[T], data: TProp):
        if clause_info.dtype is shp.Point:
            return shp.from_wkt(data)
        return data


class MySQLRepository(IRepositoryBase[MySQLConnection]):
    def get_connection(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper(self: MySQLRepository, *args, **kwargs):
            with self._pool.get_connection() as cnx:
                try:
                    return func(self, cnx._cnx, *args, **kwargs)
                except Exception as e:
                    cnx._cnx.rollback()
                    raise e

        return wrapper

    def __init__(self, **kwargs: Any) -> None:
        self._data_config: dict[str, Any] = kwargs
        self._pool: MySQLConnectionPool = self.__create_MySQLConnectionPool()

    def __create_MySQLConnectionPool(self):
        return MySQLConnectionPool(pool_name="mypool", pool_size=10, **self._data_config)

    @override
    @get_connection
    def read_sql[TFlavour](
        self,
        cnx: MySQLConnection,
        query: str,
        flavour: Type[TFlavour] = tuple,
        **kwargs,
    ) -> tuple[TFlavour]:
        """
        Return tuple of tuples by default.

        ATTRIBUTE
        -
            - query:str: string of request to the server
            - flavour: Type[TFlavour]: Useful to return tuple of any Iterable type as dict,set,list...
        """

        model: Table = kwargs.pop("model", None)
        select: Select = kwargs.pop("select", None)
        cast_to_tuple: bool = kwargs.pop("cast_to_tuple", True)

        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(query)
            values: list[tuple] = cursor.fetchall()
            columns: tuple[str] = cursor.column_names
            return Response[TFlavour](model=model, response_values=values, columns=columns, flavour=flavour, select=select).response(_tuple=cast_to_tuple, **kwargs)

    # FIXME [ ]: this method does not comply with the implemented interface
    @get_connection
    def create_tables_code_first(self, cnx: MySQLConnection, path: str | Path) -> None:
        if not isinstance(path, Path | str):
            raise ValueError

        if isinstance(path, str):
            path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError

        module_tree: ModuleTree = ModuleTree(path)

        queries_list: list[str] = module_tree.get_queries()

        for query in queries_list:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
        cnx.commit()
        return None

    @override
    @get_connection
    def executemany_with_values(self, cnx: MySQLConnection, query: str, values) -> None:
        with cnx.cursor(buffered=True) as cursor:
            cursor.executemany(query, values)
        cnx.commit()
        return None

    @override
    @get_connection
    def execute_with_values(self, cnx: MySQLConnection, query: str, values) -> None:
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(query, values)
        cnx.commit()
        return None

    @override
    @get_connection
    def execute(self, cnx: MySQLConnection, query: str) -> None:
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(query)
        cnx.commit()
        return None

    @override
    def drop_table(self, name: str) -> None:
        return DropTable(self).execute(name)

    @override
    @get_connection
    def database_exists(self, cnx: MySQLConnection, name: str) -> bool:
        query = "SHOW DATABASES LIKE %s;"
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(query, (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @override
    def drop_database(self, name: str) -> None:
        return DropDatabase(self).execute(name)

    @override
    @get_connection
    def table_exists(self, cnx: MySQLConnection, name: str) -> bool:
        if not cnx.database:
            raise Exception("No database selected")

        query = "SHOW TABLES LIKE %s;"
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(query, (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @override
    def create_database(self, name: str, if_exists: TypeExists = "fail") -> None:
        return CreateDatabase(self).execute(name, if_exists)

    @property
    def database(self) -> Optional[str]:
        return self._data_config.get("database", None)

    @database.setter
    def database(self, value: str) -> None:
        self._data_config["database"] = value
        self._pool = self.__create_MySQLConnectionPool()
