from __future__ import annotations
from typing import Type, Optional, Callable, TYPE_CHECKING, Any
import shapely as sph

if TYPE_CHECKING:
    from .table_constructor import Field


class Column[T]:
    CHAR: str = "%s"

    __slots__ = (
        "dtype",
        "column_name",
        "column_value",
        "is_primary_key",
        "is_auto_generated",
        "is_auto_increment",
        "is_unique",
    )

    def __init__(
        self,
        dtype: Type[T] = None,
        column_name: str = None,
        column_value: T = None,
        *,
        is_primary_key: bool = False,
        is_auto_generated: bool = False,
        is_auto_increment: bool = False,
        is_unique: bool = False,
    ) -> None:
        self.dtype = dtype
        self.column_name = column_name
        self.column_value: T = column_value
        self.is_primary_key: bool = is_primary_key
        self.is_auto_generated: bool = is_auto_generated
        self.is_auto_increment: bool = is_auto_increment
        self.is_unique: bool = is_unique

    @property
    def column_value_to_query(self) -> T:
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
    def placeholder_resolutor(self) -> Callable[[Type, T], str]:
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

    def __repr__(self) -> str:
        return f"<Column: {self.dtype}>"

    def __to_string__(self, field: Field):
        column_class_string: str = f"{Column.__name__}[{field.type_name}]("

        dicc: dict[str, Callable[[Field], str]] = {
            "dtype": lambda field: field.type_name,
            "column_name": lambda field: f"'{field.name}'",
            "column_value": lambda field: field.name,  # must be the same variable name as the instance variable name in Table's __init__ class
        }
        for self_var in self.__init__.__annotations__:
            if not hasattr(self, self_var):
                continue

            self_value = dicc.get(self_var, lambda field: getattr(self, self_var))(field)
            column_class_string += f" {self_var}={self_value}, "

        column_class_string += ")"
        return column_class_string

    def __hash__(self) -> int:
        return hash(
            (
                self.column_name,
                self.column_value,
                self.is_primary_key,
                self.is_auto_generated,
                self.is_auto_increment,
                self.is_unique,
            )
        )

    def __eq__(self, value: "Column") -> bool:
        if isinstance(value, Column):
            return self.__hash__() == value.__hash__()
        return False
