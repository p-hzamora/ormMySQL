from abc import ABC, abstractmethod
from typing import Literal, Optional, Type

TypeExists = Literal["fail", "replace", "append"]


class IRepositoryBase[T](ABC):
    def __repr__(self) -> str:
        return f"{IRepositoryBase.__name__}: {self.__class__.__name__}"

    @abstractmethod
    def read_sql[TFlavour](self, cnx: T, query: str, flavour: Optional[Type[TFlavour]], **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def executemany_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute(self, query: str) -> None: ...

    @abstractmethod
    def drop_database(self, name: str) -> None: ...

    @abstractmethod
    def create_database(self, name: str, if_exists: TypeExists = "fail") -> None: ...

    @abstractmethod
    def drop_table(self, name: str) -> None: ...

    @abstractmethod
    def table_exists(self, name: str) -> bool: ...

    @abstractmethod
    def database_exists(self, name: str) -> bool: ...

    @property
    @abstractmethod
    def database(self) -> Optional[str]: ...
