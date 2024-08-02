from abc import abstractmethod
from orm.common.interfaces import IQuery


class INonQueryCommand(IQuery):
    """ Interface to queries that does not retrieve any element such as insert, update, delete, etc..."""
    @abstractmethod
    def execute(self) -> None: ...