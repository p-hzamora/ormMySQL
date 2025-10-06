from __future__ import annotations
import abc

from ormlambda.sql.context import FKChain


class ColumnTableProxy(abc.ABC):
    _path: FKChain

    def __init__(self, path: FKChain):
        self._path = path

    @property
    def path(self) -> FKChain:
        return self._path

    @path.setter
    def path(self, value: FKChain) -> None:
        self._path = value
        return None

    @abc.abstractmethod
    def get_table_chain(self): ...
