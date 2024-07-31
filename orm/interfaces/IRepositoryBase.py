from abc import ABC, abstractmethod

from typing import Optional, Type


class IRepositoryBase[T](ABC):
    # @abstractmethod
    # def connect(self) -> Self: ...

    # @abstractmethod
    # def close_connection(self) -> None: ...

    @abstractmethod
    def read_sql[TFlavour](self, query: str, flavour: Optional[Type[TFlavour]], **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def executemany_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute_with_values(self, query: str, values) -> None: ...

    @property
    def connection(self) -> T: ...
