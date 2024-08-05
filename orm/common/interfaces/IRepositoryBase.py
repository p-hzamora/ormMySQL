from abc import ABC, abstractmethod
import functools
from typing import Any, Callable, Optional, Type


class IRepositoryBase[T](ABC):
    @staticmethod
    def check_connection(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper(self: "IRepositoryBase[T]", *args, **kwargs):
            if not self.is_connected():
                self.connect()

            foo = func(self, *args, **kwargs)
            self.close_connection()
            return foo

        return wrapper

    def __repr__(self) -> str:
        return f"{IRepositoryBase.__name__}: {self.__class__.__name__}"
    
    @abstractmethod
    def is_connected(self) -> bool: ...

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
    @abstractmethod
    def connection(self) -> T: ...

    @abstractmethod
    def set_config(self, value: dict[str, Any]) -> dict[str, Any]:
        """Method to update database config"""
        ...
