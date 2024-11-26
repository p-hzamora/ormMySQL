from __future__ import annotations
from typing import Type, Optional, Callable, TYPE_CHECKING, Any
import shapely as sph

from ormlambda.types import TableType, ComparerType

if TYPE_CHECKING:
    from ormlambda import Table


from .comparer import Comparer


class Column[TProp]:
    CHAR: str = "%s"
    PRIVATE_CHAR: str = "_"

    __slots__ = (
        "dtype",
        "column_name",
        "table",
        "is_primary_key",
        "is_auto_generated",
        "is_auto_increment",
        "is_unique",
        "__private_name",
    )

    def __init__[T](
        self,
        dtype: Type[TProp],
        is_primary_key: bool = False,
        is_auto_generated: bool = False,
        is_auto_increment: bool = False,
        is_unique: bool = False,
    ) -> None:
        self.dtype: Type[TProp] = dtype
        self.table: Optional[TableType[T]] = None
        # self.column_value: Optional[TProp] = None
        self.column_name: Optional[str] = None
        self.__private_name: Optional[str] = None

        self.is_primary_key: bool = is_primary_key
        self.is_auto_generated: bool = is_auto_generated
        self.is_auto_increment: bool = is_auto_increment
        self.is_unique: bool = is_unique

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.dtype}]"

    def __str__(self) -> str:
        return self.table.__table_name__ + "." + self.column_name

    def __set_name__[T: Table](self, owner: TableType[T], name):
        self.table = owner
        self.column_name = name
        self.__private_name = self.PRIVATE_CHAR + name

    def __get__(self, obj, objtype=None) -> Column[TProp] | TProp:
        if not obj:
            return self
        return getattr(obj, self.__private_name)

    def __set__(self, obj, value):
        if value is not None:
            assert type(value) == self.dtype
        setattr(obj, self.__private_name, value)

    # FIXME [ ]: this method is allocating the Column class with MySQL database
    @property
    def column_value_to_query(self) -> TProp:
        """
        This property must ensure that any variable requiring casting by different database methods is properly wrapped.
        """
        if self.dtype is sph.Point:
            return sph.to_wkt(self.column_value, -1)
        return self.column_value

    @property
    def placeholder(self) -> str:
        return self.placeholder_resolutor(self.dtype)

    @property
    def placeholder_resolutor(self) -> Callable[[Type, TProp], str]:
        return self.__fetch_wrapped_method

    # FIXME [ ]: this method is allocating the Column class with MySQL database
    @classmethod
    def __fetch_wrapped_method(cls, type_: Type) -> Optional[str]:
        """
        This method must ensure that any variable requiring casting by different database methods is properly wrapped.
        """
        caster: dict[Type[Any], Callable[[str], str]] = {
            sph.Point: lambda x: f"ST_GeomFromText({x})",
        }
        return caster.get(type_, lambda x: x)(cls.CHAR)

    def __hash__(self) -> int:
        return hash(
            (
                self.column_name,
                self.is_primary_key,
                self.is_auto_generated,
                self.is_auto_increment,
                self.is_unique,
            )
        )

    def __comparer_creator(self, other: Any, compare: ComparerType, *args) -> Comparer:
        return Comparer(self, other, compare, *args)

    def __eq__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, "=", *args)

    def __ne__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, "!=", *args)

    def __lt__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, "<", *args)

    def __le__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, "<=", *args)

    def __gt__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, ">", *args)

    def __ge__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, ">=", *args)

    def __contains__(self, other: TProp, *args) -> Comparer:
        return self.__comparer_creator(other, "in", *args)
