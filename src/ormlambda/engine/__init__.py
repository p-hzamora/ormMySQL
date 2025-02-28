from __future__ import annotations
from pathlib import Path
from typing import Any, Concatenate, Iterable, Optional, Type, override, Callable, Protocol, TypeVar, Generic, cast, TYPE_CHECKING
import contextlib
import shapely as shp

# Imports for MySQL
from mysql.connector import MySQLConnection, Error  # noqa: F401
from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionPool  # noqa: F401

# Custom libraries
from ormlambda import IRepositoryBase
from ormlambda.utils.module_tree.dynamic_module import ModuleTree

from .clauses import CreateDatabase, TypeExists, DropDatabase, DropTable

if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo
    from ormlambda import Table
    from ormlambda.databases.my_sql.clauses.select import Select

# Define type variables for type hints
TConn = TypeVar('TConn')  # Generic connection type
TFlavour = TypeVar('TFlavour', bound=Iterable)  # For response types
Ts = TypeVar('Ts')  # For tuple parameters in response

# Type alias for response types
type TResponse[TFlavour, *Ts] = TFlavour | tuple[dict[str, tuple[*Ts]]] | tuple[tuple[*Ts]] | tuple[TFlavour]

# Protocol for database connections
class DBConnection(Protocol):
    def cursor(self, **kwargs): ...
    def commit(self): ...
    def rollback(self): ...
    
# Protocol for connection pools
class ConnectionPool(Protocol, Generic[TConn]):
    @contextlib.contextmanager
    def get_connection(self) -> TConn: ...


class Response[TFlavour, *Ts]:
    def __init__(self, response_values: list[tuple[*Ts]], columns: tuple[str], flavour: Type[TFlavour], model: Optional[Table] = None, select: Optional[Select] = None) -> None:
        self._response_values: list[tuple[*Ts]] = response_values
        self._columns: tuple[str] = columns
        self._flavour: Type[TFlavour] = flavour
        self._model: Table = model
        self._select: Select = select

        self._response_values_index: int = len(self._response_values)

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

        selector.get(dict)()
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


# MySQL specific connection pool implementation
class MySQLPoolAdapter:
    def __init__(self, pool: MySQLConnectionPool):
        self._pool = pool
    
    @contextlib.contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._pool.get_connection()
            yield conn._cnx  # Access the underlying connection
        except Exception as e:
            if conn and conn._cnx:
                conn._cnx.rollback()
            raise e
        finally:
            if conn:
                conn.close()


class BaseRepository(Generic[TConn]):
    """Base repository class that can work with different database connections"""
    
    def __init__(self, pool: ConnectionPool[TConn]):
        self._pool = pool
    
    @contextlib.contextmanager
    def connection(self) -> TConn:
        """Context manager for database connections"""
        with self._pool.get_connection() as conn:
            try:
                yield conn
            except Exception as e:
                # This assumes connection has rollback method - might need to adjust based on DB type
                if hasattr(conn, 'rollback'):
                    conn.rollback()
                raise e


class MySQLRepository(BaseRepository[MySQLConnection], IRepositoryBase[MySQLConnection]):
    def __init__(self, **kwargs: str) -> None:
        self._data_config: dict[str, str] = kwargs
        mysql_pool = self.__create_MySQLConnectionPool()
        pool_adapter = MySQLPoolAdapter(mysql_pool)
        super().__init__(pool_adapter)
        
    def __create_MySQLConnectionPool(self):
        return MySQLConnectionPool(pool_name="mypool", pool_size=10, **self._data_config)

    @override
    def read_sql[TFlavour: Iterable](
        self,
        query: str,
        flavour: tuple | Type[TFlavour] = tuple,
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

        with self.connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
                values: list[tuple] = cursor.fetchall()
                columns: tuple[str] = cursor.column_names
                return Response[TFlavour](model=model, response_values=values, columns=columns, flavour=flavour, select=select).response(_tuple=cast_to_tuple, **kwargs)

    def create_tables_code_first(self, path: str | Path) -> None:
        if not isinstance(path, Path | str):
            raise ValueError

        if isinstance(path, str):
            path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError

        module_tree: ModuleTree = ModuleTree(path)
        queries_list: list[str] = module_tree.get_queries()

        with self.connection() as cnx:
            for query in queries_list:
                with cnx.cursor(buffered=True) as cursor:
                    cursor.execute(query)
            cnx.commit()
        return None

    @override
    def executemany_with_values(self, query: str, values) -> None:
        with self.connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.executemany(query, values)
            cnx.commit()
        return None

    @override
    def execute_with_values(self, query: str, values) -> None:
        with self.connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query, values)
            cnx.commit()
        return None

    @override
    def execute(self, query: str) -> None:
        with self.connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
            cnx.commit()
        return None

    @override
    def drop_table(self, name: str) -> None:
        return DropTable(self).execute(name)

    @override
    def database_exists(self, name: str) -> bool:
        with self.connection() as cnx:
            query = "SHOW DATABASES LIKE %s;"
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query, (name,))
                res = cursor.fetchmany(1)
            return len(res) > 0

    @override
    def drop_database(self, name: str) -> None:
        return DropDatabase(self).execute(name)

    @override
    def table_exists(self, name: str) -> bool:
        with self.connection() as cnx:
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
        # Recreate the pool with the new database
        mysql_pool = self.__create_MySQLConnectionPool()
        self._pool = MySQLPoolAdapter(mysql_pool)


# Example of how to extend for PostgreSQL
"""
class PostgreSQLPoolAdapter:
    def __init__(self, pool):
        self._pool = pool
    
    @contextlib.contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self._pool.putconn(conn)

class PostgreSQLRepository(BaseRepository[SomePostgreSQLConnType], IRepositoryBase[SomePostgreSQLConnType]):
    def __init__(self, **kwargs: str) -> None:
        self._data_config: dict[str, str] = kwargs
        pg_pool = self.__create_PostgreSQLConnectionPool()
        pool_adapter = PostgreSQLPoolAdapter(pg_pool)
        super().__init__(pool_adapter)
        
    def __create_PostgreSQLConnectionPool(self):
        # Create and return a PostgreSQL connection pool
        pass
        
    # Implement the rest of the IRepositoryBase methods
"""