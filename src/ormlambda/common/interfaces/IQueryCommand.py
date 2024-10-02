from abc import abstractmethod, ABC


class IQuery(ABC):
    """Interface to queries that retrieve any element such as select, limit, offset, where, group by, etc..."""

    @property
    @abstractmethod
    def query(self) -> str: ...

    def __repr__(self) -> str:
        return f"{IQuery.__name__}: {self.__class__.__name__}"
