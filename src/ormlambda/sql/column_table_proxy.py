from __future__ import annotations
import abc

from ormlambda.sql.context import FKChain

class ColumnTableProxy(abc.ABC):
    _path: FKChain

    def __init__(self, path: FKChain):
        self._path = path

    @abc.abstractmethod
    def _get_full_reference(self): ...