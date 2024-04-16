from abc import ABC, abstractmethod

from typing import Iterator, Literal, Self, overload
import pandas as pd


type_exists = Literal["fail", "replace", "append"]


class IRepositoryBase(ABC):
    @abstractmethod
    def connect(self) -> Self: ...

    @abstractmethod
    def close_connection(self) -> None: ...

    @abstractmethod
    def create_database(self, db_name: str, if_exists: type_exists = "fail") -> bool: ...

    @abstractmethod
    def drop_database(self, db_name: str) -> bool: ...

    @abstractmethod
    def create_tables(self, tables: Iterator) -> list[bool]: ...

    @abstractmethod
    def create_table(self, data: str | pd.DataFrame, name: str = None, if_exists: type_exists = "fail") -> bool: ...

    @abstractmethod
    def drop_table(self, name: str) -> bool: ...

    @overload
    def read_sql[T](self, query: str, flavour: T) -> T: ...

    @overload
    def delete(self, table: str, col: str, value: list[str]) -> None: ...
    @abstractmethod
    def delete(self, table: str, col: str, value: str) -> None: ...

    @overload
    def upsert[T](self, table, changes: dict[str, T]) -> T:
        """

        Funcion utilizada para realizar INSERT INTO o UPDATE en una misma consulta.-

        ARGS
        ----

        - table (str):  Nombre de la tabla a actualizar
        - changes (dict[str,Any]): Elemento clave/valor a actualizar

        Internamente, la funcion procedera a convertir el diccionario en una lista de diccionarios para poder realizar correctamente la consulta
        """
        ...

    @overload
    def upsert[T](self, table, changes: list[dict[str, T]]) -> T:
        """
        Funcion utilizada para realizar INSERT INTO o UPDATE en una misma consulta.

        ARGS
        ----

        - table (str):  Nombre de la tabla a actualizar
        - changes (list[dict[str,Any]]): Elemento clave/valor a actualizar"""
        ...

    @overload
    def upsert(self, table, changes: pd.DataFrame) -> pd.DataFrame:
        """
        Funcion utilizada para realizar INSERT INTO o UPDATE en una misma consulta.

        ARGS
        ----

        - table (str):  Nombre de la tabla a actualizar
        - changes (pd.DataFrame): Elemento clave/valor a actualizar"""
        ...

    @abstractmethod
    def upsert[T](self, table: str, changes: dict[str, T] | list[T] | pd.DataFrame) -> None: ...

    @abstractmethod
    def insert[T](self, table: str, values: list[T] | pd.DataFrame) -> None: ...
