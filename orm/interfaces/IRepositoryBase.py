from abc import ABC, abstractmethod

from typing import Literal, Optional, Type, overload


class IRepositoryBase[T](ABC):
    # @abstractmethod
    # def connect(self) -> Self: ...

    # @abstractmethod
    # def close_connection(self) -> None: ...

    @abstractmethod
    def create_database(self, db_name: str, if_exists: type_exists = "fail") -> bool: ...

    @abstractmethod
    def drop_database(self, db_name: str) -> bool: ...

    @abstractmethod
    def drop_table(self, name: str) -> bool: ...

    @overload
    def read_sql(self, query: str) -> tuple[tuple]: ...

    @overload
    def executemany_with_values(self, query: str, values) -> None: ...
    
    @overload
    def execute_with_values(self, query: str, values) -> None: ...
    
    @overload
    def read_sql[TFlavour](self, query: str, flavour: Optional[Type[TFlavour]], **kwargs) -> tuple[TFlavour]: ...
