from __future__ import annotations
from typing import Generator, Optional, Type, Unpack, TYPE_CHECKING
from ormlambda.repository import IRepositoryBase
import abc

if TYPE_CHECKING:
    from ormlambda import URL as _URL
    from ormlambda.dialects.interface.dialect import Dialect


class BaseRepository[TPool](IRepositoryBase):
    def __init__[TArgs](
        self,
        /,
        url: Optional[_URL] = None,
        *,
        dialect: Optional[Dialect] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        database: Optional[str] = None,
        pool: Optional[Type[TPool]] = None,
        **kwargs: Unpack[TArgs],
    ) -> None:
        self._dialect = dialect
        self._url = url

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
