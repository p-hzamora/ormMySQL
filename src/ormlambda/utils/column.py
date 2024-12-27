from __future__ import annotations
from typing import Type, Optional, TYPE_CHECKING
import abc
from ormlambda.types import TableType, ComparerType, ColumnType
from ormlambda import ConditionType

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.common.abstract_classes.comparer import Comparer, Regex, Like


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

    def __init__[T: Table](
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
        return f"{type(self).__name__}[{self.dtype.__name__}](name='{self.column_name}')"

    def __str__(self) -> str:
        return self.table.__table_name__ + "." + self.column_name

    def __set_name__[T: Table](self, owner: TableType[T], name: str) -> None:
        self.table: TableType[T] = owner
        self.column_name = name
        self.__private_name = self.PRIVATE_CHAR + name

    def __get__(self, obj, objtype=None) -> Column[TProp] | TProp:
        if not obj:
            return self
        return getattr(obj, self.__private_name)

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, self.dtype):
                raise ValueError(f"The '{self.column_name}' Column from '{self.table.__table_name__}' table expected '{str(self.dtype)}' type. You passed '{type(value).__name__}' type")
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
    def __comparer_creator[LTable: Table, OTherTable: Table, OTherType](self, other: ColumnType[OTherType], compare: ComparerType, *args) -> Comparer:
        from ormlambda.common.abstract_classes.comparer import Comparer

        return Comparer[LTable, TProp, OTherTable, OTherType](self, other, compare, *args)

    def __eq__[LTable, OTherTable, OTherProp](self, other: ColumnType[OTherProp], *args) -> Comparer[LTable, TProp, OTherTable, OTherProp]:
        return self.__comparer_creator(other, ConditionType.EQUAL.value, *args)

    def __ne__[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.NOT_EQUAL.value, *args)

    def __lt__[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.LESS_THAN.value, *args)

    def __le__[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.LESS_THAN_OR_EQUAL.value, *args)

    def __gt__[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.GREATER_THAN.value, *args)

    def __ge__[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.GREATER_THAN_OR_EQUAL.value, *args)

    def contains[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.IN.value, *args)

    def not_contains[LTable, OTherTable, OtherProp](self, other: ColumnType[OtherProp], *args) -> Comparer[LTable, TProp, OTherTable, OtherProp]:
        return self.__comparer_creator(other, ConditionType.NOT_IN.value, *args)

    def regex[LProp, RProp](self, pattern: str) -> Regex[LProp, RProp]:
        from ormlambda.common.abstract_classes.comparer import Regex

        return Regex(self, pattern)

    def like[LProp, RProp](self, pattern: str) -> Like[LProp, RProp]:
        from ormlambda.common.abstract_classes.comparer import Like

        return Like(self, pattern)
