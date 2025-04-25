from typing import Generator, Optional, Type, Unpack
from ormlambda.repository import IRepositoryBase
import abc


class BaseRepository[TPool](IRepositoryBase):
    def __init__[TArgs](
        self,
        *,
        user: str,
        password: str,
        host: str,
        database: Optional[str] = None,
        pool: Optional[Type[TPool]] = None,
        **kwargs: Unpack[TArgs],
    ) -> None:
        self._user = user
        self._password = password
        self._host = host
        self._database = database

        if pool:
            attr = {
                "user": self._user,
                "password": self._password,
                "host": self._host,
                "database": self._database,
                **kwargs,
            }
            self._pool: TPool = pool(**attr)

    @abc.abstractmethod
    def get_connection[TCnx](self) -> Generator[TCnx, None, None]: ...
