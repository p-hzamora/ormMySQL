from __future__ import annotations
from pathlib import Path
import sqlite3
import contextlib
from typing import Generator, Iterable, Optional, Type, TYPE_CHECKING
from ormlambda import BaseRepository
from ormlambda.repository.response import Response
from ormlambda.caster import Caster

if TYPE_CHECKING:
    from ormlambda.sql.clauses import _Select


class SQLiteRepository(BaseRepository):
    def __init__(
        self,
        *,
        user,
        password,
        host,
        database=None,
        **kwargs,
    ):
        super().__init__(
            user=user,
            password=password,
            host=host,
            database=database,
            pool=None,
            **kwargs,
        )

    @contextlib.contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            cnx = sqlite3.connect(self.database)
            yield cnx
            cnx.commit()
        finally:
            cnx.close()

    def read_sql[TFlavour: Iterable](
        self,
        query: str,
        flavour: tuple | Type[TFlavour] = tuple,
        **kwargs,
    ) -> tuple[TFlavour]:
        select: _Select = kwargs.pop("select", None)

        with self.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(query)
            values: list[tuple] = cursor.fetchall()
            columns: tuple[str] = tuple([x[0] for x in cursor.description])
            return Response(
                repository=self,
                response_values=values,
                columns=columns,
                flavour=flavour,
                select=select,
            ).response(**kwargs)

    def executemany_with_values(self, query: str, values) -> None:
        with self.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.executemany(query, values)
        return None

    def execute_with_values(self, query: str, values) -> None:
        with self.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(query, values)
        return None

    def execute(self, query: str) -> None:
        with self.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(query)
        return None

    def drop_table(self, name: str) -> None:
        self.execute(f"DROP TABLE IF EXISTS {name};")
        return None

    def database_exists(self, name: str) -> bool:
        res = self.read_sql("SELECT name FROM sqlite_master", flavour=tuple)
        if not res:
            return False

        return name in res[0]

    def drop_database(self, name: str = "") -> None:
        Path(self.database).unlink()

    def table_exists(self, name: str) -> bool:
        with self.get_connection() as cnx:
            cursor = cnx.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name={Caster.PLACEHOLDER};", (name,))
            res = cursor.fetchmany(1)
        return len(res) > 0

    def create_database(self, name: str = "", if_exists="fail") -> None:
        return None

    @property
    def database(self) -> Optional[str]:
        return self._database
