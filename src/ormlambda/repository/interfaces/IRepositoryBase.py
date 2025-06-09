from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    Annotated,
    Any,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Type,
    Iterable,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from ormlambda.statements.types import TypeExists


type _DBAPICursorDescription = Sequence[
    tuple[
        Annotated[str, "name"],
        Annotated[str, "type_code"],
        Annotated[Optional[str], "display_size"],
        Annotated[Optional[str], "internal_size"],
        Annotated[Optional[str], "precision"],
        Annotated[Optional[str], "scale"],
        Annotated[Optional[str], "null_ok"],
    ]
]


type _GenericSequence = Sequence[Any]

type _CoreSingleExecuteParams = Mapping[str, Any]
type _CoreMultiExecuteParams = Sequence[_CoreSingleExecuteParams]

type _DBAPISingleExecuteParams = _GenericSequence | _CoreSingleExecuteParams
type _DBAPIMultiExecuteParams = Sequence[_GenericSequence] | _CoreMultiExecuteParams


class DBAPICursor(Protocol):
    """protocol representing a :pep:`249` database cursor.

    .. versionadded:: 2.0

    .. seealso::

        `Cursor Objects <https://www.python.org/dev/peps/pep-0249/#cursor-objects>`_
        - in :pep:`249`

    """  # noqa: E501

    @property
    def description(
        self,
    ) -> _DBAPICursorDescription:
        """The description attribute of the Cursor.

        .. seealso::

            `cursor.description <https://www.python.org/dev/peps/pep-0249/#description>`_
            - in :pep:`249`


        """  # noqa: E501
        ...

    @property
    def rowcount(self) -> int: ...

    arraysize: int

    lastrowid: int

    def close(self) -> None: ...

    def execute(
        self,
        operation: Any,
        parameters: Optional[_DBAPISingleExecuteParams] = None,
    ) -> Any: ...

    def executemany(
        self,
        operation: Any,
        parameters: _DBAPIMultiExecuteParams,
    ) -> Any: ...

    def fetchone(self) -> Optional[Any]: ...

    def fetchmany(self, size: int = ...) -> Sequence[Any]: ...

    def fetchall(self) -> Sequence[Any]: ...

    def setinputsizes(self, sizes: Sequence[Any]) -> None: ...

    def setoutputsize(self, size: Any, column: Any) -> None: ...

    def callproc(self, procname: str, parameters: Sequence[Any] = ...) -> Any: ...

    def nextset(self) -> Optional[bool]: ...

    def __getattr__(self, key: str) -> Any: ...


class DBAPIConnection(Protocol):
    """protocol representing a :pep:`249` database connection.

    .. versionadded:: 2.0

    .. seealso::

        `Connection Objects <https://www.python.org/dev/peps/pep-0249/#connection-objects>`_
        - in :pep:`249`

    """  # noqa: E501

    def close(self) -> None: ...

    def commit(self) -> None: ...

    def cursor(self) -> DBAPICursor: ...

    def rollback(self) -> None: ...

    autocommit: bool


class IRepositoryBase(ABC):
    def __repr__(self) -> str:
        return f"{IRepositoryBase.__name__}: {self.__class__.__name__}"

    @abstractmethod
    def read_sql[TFlavour: Iterable](self, query: str, flavour: Optional[Type[TFlavour]], **kwargs) -> tuple[TFlavour]: ...

    @abstractmethod
    def executemany_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute_with_values(self, query: str, values) -> None: ...

    @abstractmethod
    def execute(self, query: str) -> None: ...

    @abstractmethod
    def drop_table(self, name: str) -> None: ...

    @abstractmethod
    def table_exists(self, name: str) -> bool: ...

    @abstractmethod
    def database_exists(self, name: str) -> bool: ...

    @property
    @abstractmethod
    def database(self) -> Optional[str]: ...
