from __future__ import annotations
import abc
from ormlambda.common.interfaces import IQuery
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ormlambda.sql.clause_info import ClauseInfo

class ISelect(IQuery):
    @property
    @abc.abstractmethod
    def FROM(self)->ClauseInfo: ...
    
    @property
    @abc.abstractmethod
    def COLUMNS(self)->str: ...

