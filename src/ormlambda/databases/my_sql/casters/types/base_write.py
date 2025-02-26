import abc


class IWrite[T](abc.ABC):
    @abc.abstractmethod
    def cast(value: T) -> str: ...
