from abc import abstractmethod, ABC


class IQuery(ABC):
    @property
    @abstractmethod
    def query(self) -> str: ...
