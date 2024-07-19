# Standard libraries
from functools import wraps
from pathlib import Path
from typing import Any, Iterator, Literal, Type, override

# Third party libraries
import pandas as pd

from mysql.connector import connection, Error
from mysql.connector import errorcode

# Custom libraries
from .interfaces import IRepositoryBase
from .orm_objects.table import Table, Column
from .orm_objects.foreign_key import ForeignKey
from .dynamic_module import ModuleTree
from .dtypes import get_query_clausule

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


class MySQLRepository(IRepositoryBase):
    def is_connected(func):
        @wraps(func)
        def wrapper(self: "MySQLRepository", *args, **kwargs):
            if not self._connection.is_connected():
                self.connect()

            foo = func(self, *args, **kwargs)
            self.close_connection()
            return foo

        return wrapper

    def __init__(
        self,
        user: str,
        password: str,
        database: str = None,
        port: str = "3306",
        host: str = "localhost",
    ) -> None:
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._host = host

        self._connection: connection.MySQLConnection = None

    @property
    @override
    def database(self) -> str:
        return self._connection.database

    @database.setter
    @is_connected
    def database(self, value: str) -> None:
        self._connection.database = value

    @property
    @override
    def port(self) -> str:
        return self._port

    @property
    @override
    def host(self) -> str:
        return self._host

    def connect(self) -> "MySQLRepository":
        self._connection = connection.MySQLConnection(
            user=self._user,
            password=self._password,
            database=self._database,
            port=self._port,
            host=self._host,
        )
        return self

    def close_connection(self) -> None:
        if self._connection.is_connected():
            self._connection.close()
        return None

    @is_connected
    def create_database(self, db_name: str, if_exists: Literal["fail", "replace"] = "fail") -> None:
        self._database = db_name
        with self._connection.cursor() as cursor:
            try:
                cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
            except Error as err:
                if err.errno == errorcode.ER_DB_CREATE_EXISTS and if_exists != "fail":
                    cursor.execute(f"USE {db_name};")
                else:
                    raise err
            else:
                self._connection.database = db_name
        return None

    @is_connected
    def drop_database(self, db_name: str):
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE {db_name}")
        except Error as err:
            raise err

    def create_tables(self, tables: Iterator):
        for table_name in tables:
            table_description = tables[table_name]
            self.create_table(table_description)

    @is_connected
    def create_table(
        self,
        data: str | pd.DataFrame,
        name: str = None,
        if_exists: type_exists = "fail",
    ) -> bool:
        def translate_dtypes(series: pd.Series):
            dtypes = {"float64": "DOUBLE"}

            if str(series.dtype) == "object":
                dtype = f"VARCHAR({series.astype('str').str.len().max()})"
            elif str(series.dtype) == "int64":
                max_int = series.max()
                if max_int <= 127:
                    dtype = "TINYINT"
                elif max_int <= 32767:
                    dtype = "SMALLINT"
                elif max_int <= 8388607:
                    dtype = "MEDIUMINT"
                elif max_int <= 2147483647:
                    dtype = "INT"
                else:
                    dtype = "BIGINT"
            else:
                dtype = dtypes.get(str(series.dtype))
            return dtype

        # ____________________________________________start____________________________________________
        if isinstance(data, pd.DataFrame):
            params_column_dtype = []
            # CREATE TABLE params preparation
            for column_name, series in data.items():
                dtype = translate_dtypes(series)
                params_column_dtype.append(f"{column_name} {dtype}")

            query = f"""CREATE TABLE {name} ({', '.join(params_column_dtype)});"""
            # recursion
            if self.create_table(query, name=name, if_exists=if_exists):
                # try insert values
                self.insert(name, data.to_dict("records"))
                return True

        with self._connection.cursor(buffered=True) as cursor:
            # try create table
            try:
                cursor.execute(data)
                self._connection.commit()
            except Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR and if_exists != "fail":
                    if if_exists == "replace":
                        cursor.execute(f"DROP TABLE {name}")
                        self.create_table(data, name, if_exists="fail")
                        return True
                    else:
                        raise err
                else:
                    raise err
        return True

    @is_connected
    def drop_table(self, name: str) -> bool:
        query = rf"DROP TABLE {name}"
        # CONSULTA A LA BBDD
        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            self._connection.commit()
        return True

    @is_connected
    def read_sql[TFlavour](self, query: str, flavour: Type[TFlavour] = tuple, **kwargs) -> tuple[TFlavour]:
        """ """

        with self._connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            values: list[tuple] = cursor.fetchall()
            columns: tuple[str] = cursor.column_names
            return Response[TFlavour](response_values=values, columns=columns, flavour=flavour, **kwargs).response

    @is_connected
    def delete(self, table: str, col: str, value: list[str] | str) -> None:
        with self._connection.cursor() as cursor:
            if isinstance(value, str):
                cursor.execute(f"DELETE FROM {table} WHERE {col} = %s", (value,))
            elif isinstance(value, list):
                params = ", ".join(["%s"] * len(value))
                cursor.execute(f"DELETE FROM {table} WHERE {col} IN ({params})", value)
            else:
                raise Exception(f"'{type(value)}' no esperado")
            self._connection.commit()
        return None

    @staticmethod
    def _clean_data(data: list[dict[str, Any]]) -> list[tuple]:
        res = []
        for x in data:
            val = list(x.values())
            for i in range(len(x)):
                try:
                    val[i] = val[i].to_pydatetime()
                except Exception:
                    continue
                if str(val[i]) == "NaT":
                    val[i] = None
            res.append(tuple(val))
        return res

    @is_connected
    def upsert(self, table: str, changes: dict[str, Any] | list[dict[str, Any]] | pd.DataFrame):
        """
        Esta funcion se enfoca para trabajar con listas, aunque el argumneto changes sea un unico diccionario.

        Accedemos a la primera posicion de la lista 'changes[0]' porque en la query solo estamos poniendo marcadores de posicion, alias y nombres de columnas

        EXAMPLE
        ------

        MySQL
        -----

        INSERT INTO NAME_TABLE(PK_COL,COL2)
        VALUES
        (1,'PABLO'),
        (2,'MARINA') AS _val
        ON DUPLICATE KEY UPDATE
        COL2 = _val.COL2;

        Python
        -----

        INSERT INTO NAME_TABLE(PK_COL,COL2)
        VALUES (%s, %s') AS _val
        ON DUPLICATE KEY UPDATE
        COL2 = _val.COL2;

        """
        valid_types = (dict, list, pd.DataFrame, tuple)
        if not isinstance(changes, valid_types):
            raise ValueError(f"El tipo de dato de changes es {type(changes)}.\nSe esperaba {valid_types}")

        if isinstance(changes, dict):
            return self.upsert(table, changes=(changes,))

        if isinstance(changes, pd.DataFrame):
            return self.upsert(table, changes.to_dict("records"))

        alias = "_values"
        columns = ", ".join([f"{x}" for x in changes[0].keys()])
        position_mark = ", ".join(["%s" for _ in changes[0].values()])
        alternative = ", ".join([f"{col} = {alias}.{col}" for col in changes[0]])
        query = f"INSERT INTO {table} ({columns})" f"   VALUES ({position_mark}) as {alias}" f"   ON DUPLICATE KEY UPDATE" f"   {alternative};"

        with self._connection.cursor(buffered=True) as cursor:
            cursor.executemany(query, self._clean_data(changes))

            self._connection.commit()

        return None

    @is_connected
    def insert(self, table: str, values: list[dict[str, Any]] | pd.DataFrame) -> None:
        if isinstance(values, list):
            dicc_0 = values[0]
            col = ", ".join(dicc_0.keys())
            row = f'({", ".join(["%s"]*len(dicc_0))})'  # The number of "%s" must match the dict 'dicc_0' length

        elif isinstance(values, pd.DataFrame):
            self.insert(table, values.to_dict("records"))
            return None

        else:
            raise ValueError(f"Se esperaba una lista de diccionarios o un DataFrame no {type(values)}")

        query = f"INSERT INTO {table} {f'({col})'} VALUES {row}"
        with self._connection.cursor(buffered=True) as cursor:
            cursor.executemany(query, self._clean_data(values))
            self._connection.commit()
        return None

    # FIXME [ ]: this method does not comply with the implemented interface
    @is_connected
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
            with self._connection.cursor(buffered=True) as cursor:
                cursor.execute(query)
                self._connection.commit()
        return None

