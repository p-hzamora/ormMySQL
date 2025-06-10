from __future__ import annotations
import contextlib
from pathlib import Path
from typing import Generator, Iterable, Optional, Type, override, TYPE_CHECKING, Unpack
import uuid

# from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import MySQLConnection  # noqa: F401
from mysql.connector.pooling import MySQLConnectionPool  # noqa: F401
from ormlambda.repository import BaseRepository

# Custom libraries
from .clauses import DropTable
from ormlambda.repository.response import Response
from ormlambda.caster import Caster

if TYPE_CHECKING:
    from ormlambda import URL as _URL
    from ormlambda.sql.clauses import Select
    from .pool_types import MySQLArgs


class MySQLRepository(BaseRepository[MySQLConnectionPool]):
    # def get_connection[**P, TReturn](func: Callable[Concatenate[MySQLRepository, MySQLConnection, P], TReturn]) -> Callable[P, TReturn]:
    #     def wrapper(self: MySQLRepository, *args: P.args, **kwargs: P.kwargs):
    #         with self.get_connection() as cnx:
    #             try:
    #                 return func(self, cnx._cnx, *args, **kwargs)
    #             except Exception as e:
    #                 cnx._cnx.rollback()
    #                 raise e

    #     return wrapper

    #

    def __init__(
        self,
        /,
        url: Optional[_URL] = None,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        database: Optional[str] = None,
        **kwargs: Unpack[MySQLArgs],
    ):
        timeout = self.__add_connection_timeout(kwargs)
        name = self.__add_pool_name(kwargs)
        size = self.__add_pool_size(kwargs)
        attr = kwargs.copy()
        attr["connection_timeout"] = timeout
        attr["pool_name"] = name
        attr["pool_size"] = size

        super().__init__(
            user=user if not url else url.username,
            password=password if not url else url.password,
            host=host if not url else url.host,
            database=database if not url else url.database,
            pool=MySQLConnectionPool,
            **attr,
        )

    @staticmethod
    def __add_connection_timeout(kwargs: MySQLArgs) -> int:
        if "connection_timeout" not in kwargs.keys():
            return 60
        return int(kwargs.pop("connection_timeout"))

    @staticmethod
    def __add_pool_name(kwargs: MySQLArgs) -> str:
        if "pool_name" not in kwargs.keys():
            return str(uuid.uuid4())

        return kwargs.pop("pool_name")

    @staticmethod
    def __add_pool_size(kwargs: MySQLArgs) -> int:
        if "pool_size" not in kwargs.keys():
            return 5
        return int(kwargs.pop("pool_size"))

    @contextlib.contextmanager
    def get_connection(self) -> Generator[MySQLConnection, None, None]:
        with self._pool.get_connection() as cnx:
            try:
                yield cnx._cnx
                cnx._cnx.commit()
            except Exception as exc:
                cnx._cnx.rollback()
                raise exc

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

        select: Select = kwargs.pop("select", None)

        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
                values: list[tuple] = cursor.fetchall()
                columns: tuple[str] = cursor.column_names
                return Response(
                    dialect=self._dialect,
                    response_values=values,
                    columns=columns,
                    flavour=flavour,
                    select=select,
                ).response(**kwargs)

    # FIXME [ ]: this method does not comply with the implemented interface
    def create_tables_code_first(self, path: str | Path) -> None:
        return
        from ormlambda.utils.module_tree.dynamic_module import ModuleTree

        if not isinstance(path, Path | str):
            raise ValueError

        if isinstance(path, str):
            path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError

        module_tree: ModuleTree = ModuleTree(path)

        queries_list: list[str] = module_tree.get_queries()

        for query in queries_list:
            with self.get_connection() as cnx:
                with cnx.cursor(buffered=True) as cursor:
                    cursor.execute(query)
        return None

    @override
    def executemany_with_values(self, query: str, values) -> None:
        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.executemany(query, values)
        return None

    @override
    def execute_with_values(self, query: str, values) -> None:
        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query, values)
        return None

    @override
    def execute(self, query: str) -> None:
        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
        return None

    @override
    def drop_table(self, name: str) -> None:
        return DropTable(self).execute(name)

    @override
    def database_exists(self, name: str) -> bool:
        temp_config = self._pool._cnx_config

        config_without_db = temp_config.copy()

        if "database" in config_without_db:
            config_without_db.pop("database")
        self._pool.set_config(**config_without_db)

        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(f"SHOW DATABASES LIKE {Caster.PLACEHOLDER};", (name,))
                res = cursor.fetchmany(1)

        self._pool.set_config(**temp_config)
        return len(res) > 0

    @override
    def table_exists(self, name: str) -> bool:
        with self.get_connection() as cnx:
            if not cnx.database:
                raise Exception("No database selected")
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(f"SHOW TABLES LIKE {Caster.PLACEHOLDER};", (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @property
    def database(self) -> Optional[str]:
        return self._pool._cnx_config.get("database", None)

    @database.setter
    def database(self, value: str) -> None:
        """Change the current database using USE statement"""

        if not self.database_exists(value):
            raise ValueError(f"You cannot set the non-existent '{value}' database.")

        old_config: MySQLArgs = self._pool._cnx_config.copy()
        old_config["database"] = value

        self._pool._remove_connections()
        self._pool = type(self)(**old_config)._pool
