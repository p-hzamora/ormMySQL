from __future__ import annotations
import contextlib
from pathlib import Path
from typing import Any, Generator, Iterable, Optional, Type, override, TYPE_CHECKING
import shapely as shp

# from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import MySQLConnection  # noqa: F401
from mysql.connector.pooling import MySQLConnectionPool  # noqa: F401
from ormlambda.repository import BaseRepository

# Custom libraries
from ormlambda.repository import IRepositoryBase
from ormlambda.caster import Caster

from ..clauses import CreateDatabase, TypeExists
from ..clauses import DropDatabase
from ..clauses import DropTable


if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo
    from ormlambda import Table
    from ormlambda.databases.my_sql.clauses.select import Select

type TResponse[TFlavour, *Ts] = TFlavour | tuple[dict[str, tuple[*Ts]]] | tuple[tuple[*Ts]] | tuple[TFlavour]


class Response[TFlavour, *Ts]:
    def __init__(self, repository: IRepositoryBase, response_values: list[tuple[*Ts]], columns: tuple[str], flavour: Type[TFlavour], model: Optional[Table] = None, select: Optional[Select] = None) -> None:
        self._repository: IRepositoryBase = repository
        self._response_values: list[tuple[*Ts]] = response_values
        self._columns: tuple[str] = columns
        self._flavour: Type[TFlavour] = flavour
        self._model: Table = model
        self._select: Select = select

        self._response_values_index: int = len(self._response_values)
        # self.select_values()
        self._caster = Caster(repository)

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
        new_response: list[tuple] = []
        for row in self._response_values:
            new_row: list = []
            for i, data in enumerate(row):
                alias = self._columns[i]
                clause_info = self._select[alias]
                if not self._is_parser_required(clause_info):
                    new_row = row
                    break
                else:
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

    @staticmethod
    def parser_data[T: Table, TProp](clause_info: ClauseInfo[T], data: TProp):
        if clause_info.dtype is shp.Point:
            return shp.from_wkt(data)
        return data


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

    def __init__(self, **kwargs):
        super().__init__(MySQLConnectionPool, **kwargs)

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

        model: Table = kwargs.pop("model", None)
        select: Select = kwargs.pop("select", None)
        cast_to_tuple: bool = kwargs.pop("cast_to_tuple", True)

        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query)
                values: list[tuple] = cursor.fetchall()
                columns: tuple[str] = cursor.column_names
                return Response[TFlavour](
                    repository=self,
                    model=model,
                    response_values=values,
                    columns=columns,
                    flavour=flavour,
                    select=select,
                ).response(_tuple=cast_to_tuple, **kwargs)

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
        query = "SHOW DATABASES LIKE %s;"
        temp_config = self._pool._cnx_config

        config_without_db = temp_config.copy()

        if "database" in config_without_db:
            config_without_db.pop("database")
        self._pool.set_config(**config_without_db)
        with self.get_connection() as cnx:
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query, (name,))
            res = cursor.fetchmany(1)

        self._pool.set_config(**temp_config)
        return len(res) > 0

    @override
    def drop_database(self, name: str) -> None:
        return DropDatabase(self).execute(name)

    @override
    def table_exists(self, name: str) -> bool:
        query = "SHOW TABLES LIKE %s;"
        with self.get_connection() as cnx:
            if not cnx.database:
                raise Exception("No database selected")
            with cnx.cursor(buffered=True) as cursor:
                cursor.execute(query, (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    @override
    def create_database(self, name: str, if_exists: TypeExists = "fail") -> None:
        temp_config = self._pool._cnx_config

        config_without_db = temp_config.copy()

        if "database" in config_without_db:
            config_without_db.pop("database")
        return CreateDatabase(type(self)(**config_without_db)).execute(name, if_exists)

    @property
    def database(self) -> Optional[str]:
        return self._data_config.get("database", None)

    @database.setter
    def database(self, value: str) -> None:
        self._data_config["database"] = value
        self._pool.set_config(**self._data_config)
