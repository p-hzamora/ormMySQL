from abc import ABC, abstractmethod

from typing import Any, Optional, Type


class IRepositoryBase[T](ABC):
    @staticmethod
    @abstractmethod
    def is_connected(func): ...
    
    @abstractmethod
    def connect(self, **kwargs: Any) -> "IRepositoryBase[T]": ...

    @abstractmethod
    def close_connection(self) -> None: ...

    @abstractmethod
    def read_sql[TFlavour](self, query: str, flavour: Optional[Type[TFlavour]], **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def executemany_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute(self, query: str) -> None: ...

    @abstractmethod
    def drop_database(self, name: str) -> None: ...

    @abstractmethod
    def create_database(self, name: str) -> None: ...

    @abstractmethod
    def drop_table(self, name: str) -> None: ...

    @property
    def connection(self) -> T: ...
