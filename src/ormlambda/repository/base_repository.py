import contextlib
from typing import Generator, Type, Unpack
from ormlambda.repository import IRepositoryBase
import abc


class BaseRepository[TPool](IRepositoryBase):
    def __init__[TArgs](self, pool: Type[TPool], **kwargs: Unpack[TArgs]) -> None:
        self._data_config: dict[str, str] = kwargs
        self._pool: TPool = pool(**kwargs)

    @contextlib.contextmanager
    @abc.abstractmethod
    def get_connection[TCnx](self) -> Generator[TCnx, None, None]: ...
