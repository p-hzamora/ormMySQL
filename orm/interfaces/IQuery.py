from abc import abstractmethod, ABC


class IQuery(ABC):
    SEMICOLON = ";"

    @abstractmethod
    def load(self) -> str: ...

    @property
    @abstractmethod
    def query(self) -> str: ...
