import abc


class IWrite[T](abc.ABC):
    @abc.abstractmethod
    def cast(value: str | T, insert_data: bool = False) -> str: ...
