from abc import abstractmethod, ABC


class IQuery(ABC):
    @abstractmethod
    def execute (self) -> str: ...

    def __repr__(self) -> str:
        return f"{IQuery.__name__}: {self.__class__.__name__}"
