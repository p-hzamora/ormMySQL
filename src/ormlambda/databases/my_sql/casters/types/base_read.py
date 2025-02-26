import abc


class IRead[T](abc.ABC):
    @abc.abstractmethod
    def cast(value: str) -> T: ...
