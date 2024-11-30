from __future__ import annotations
from typing import Type, Optional, TYPE_CHECKING
import abc
from ormlambda.types import TableType, ComparerType, ColumnType

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.abstract_classes.comparer import Comparer


class Column[TProp]:
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

    @abc.abstractmethod
    def __comparer_creator[OTherType](self, other: ColumnType[OTherType], compare: ComparerType, *args) -> Comparer:
        from ormlambda.common.abstract_classes.comparer import Comparer

        return Comparer[TProp, OTherType](self, other, compare, *args)

    def __eq__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, "=", *args)

    def __ne__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, "!=", *args)

    def __lt__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, "<", *args)

    def __le__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, "<=", *args)

    def __gt__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, ">", *args)

    def __ge__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, ">=", *args)

    def __contains__[TOtherProp](self, other: ColumnType[TOtherProp], *args) -> Comparer[TProp, TOtherProp]:
        return self.__comparer_creator(other, "in", *args)
