from __future__ import annotations
import abc

from ormlambda.common.interfaces.IQueryCommand import IQuery


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...
