from abc import abstractmethod
from orm.common.interfaces import IQuery


class INonQueryCommand(IQuery):
    @abstractmethod
    def execute(self) -> None: ...