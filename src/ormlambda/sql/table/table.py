from __future__ import annotations
from typing import Any, Optional, Type, dataclass_transform, TYPE_CHECKING
import json

from ormlambda.sql.ddl import CreateTable, DropTable
from ormlambda import util

if TYPE_CHECKING:
    from ormlambda.sql import Column
    from ormlambda.dialects import Dialect
    from ormlambda import ForeignKey

from .table_constructor import __init_constructor__


class TableMeta(type):
    def __new__[T](cls: "Table", name: str, bases: tuple, dct: dict[str, Any]) -> Type[T]:
        """
        That's the class we use to recreate the table's metadata.
        It's useful because we can dynamically create the __init__ method just by using the type hints of the variables we want to use as column names.
        We simply call '__init_constructor__' to create all the necessary variables and the method.
        """
        cls_object: Table = super().__new__(cls, name, bases, dct)

        if name == "Table":
            return cls_object

        if cls_object.__table_name__ is Ellipsis:
            raise Exception(f"class variable '__table_name__' must be declared in '{cls_object.__name__}' class")

        if not isinstance(cls_object.__table_name__, str):
            raise Exception(f"class variable '__table_name__' of '{cls_object.__name__}' class must be 'str'")

        self = __init_constructor__(cls_object)

        return self

    def __repr__(cls: "Table") -> str:
        return f"{TableMeta.__name__}: {cls.__table_name__}"


@dataclass_transform(eq_default=False)
class Table(metaclass=TableMeta):
    """
    Class to mapped database tables with Python classes.

    It uses __annotations__ special var to store all table columns. If you do not type class var it means this var is not store as table column
    and it do not going to appear when you instantiate the object itself.

    This principle it so powerful due to we can create Foreign Key references without break __init__ class method.

    >>> class Address(Table):
    >>>     __table_name__ = "address"

    >>>     address_id: int = Column(int, is_primary_key=True)
    >>>     address: str
    >>>     address2: str
    >>>     district: str
    >>>     city_id: int
    >>>     postal_code: datetime
    >>>     phone: str
    >>>     location: datetime
    >>>     last_update: datetime = Column(datetime, is_auto_generated=True)

    >>>     city = ForeignKey["Address", City](City, lambda a, c: a.city_id == c.city_id)
    """

    __table_name__: str = ...

    def __str__(self) -> str:
        params = self.to_dict()
        return json.dumps(params, ensure_ascii=False, indent=2)

    def __getattr__[T](self, _name: str) -> Column[T]:
        return self.__dict__.get(_name, None)

    def __repr__(self: "Table") -> str:
        def __cast_long_variables(value: Any):
            if not isinstance(value, str):
                value = str(value)
            if len(value) > 20:
                return value[:20] + "..."
            return value

        dicc: dict[str, str] = {x: str(getattr(self, x)) for x in self.__annotations__}
        equal_loop = ["=".join((x, __cast_long_variables(y))) for x, y in dicc.items()]
        return f"{self.__class__.__name__}({', '.join(equal_loop)})"

    def __getitem__[TProp](self, value: str | Column[TProp]) -> Optional[TProp]:
        name = value if isinstance(value, str) else value.column_name
        if hasattr(self, name):
            return getattr(self, name)
        return None

    def to_dict(self) -> dict[str, str | int]:
        def make_hashable(item: Any) -> Any:
            if isinstance(item, dict):
                return tuple(sorted((k, make_hashable(x)) for k, x in item.items()))

            if isinstance(item, (list | set)):
                return tuple(make_hashable(x) for x in item)
            if hasattr(item, "__iter__") and not isinstance(item, str | bytes):
                try:
                    return tuple(make_hashable(x) for x in item)
                except TypeError:
                    return item  # if it fails, it's already hashable
            return item

        dicc: dict[str, Any] = {}
        for x in self.__annotations__:
            value = getattr(self, x)
            dicc[x] = make_hashable(value)
        return dicc

    @util.preload_module("ormlambda.sql")
    @classmethod
    def get_pk(cls) -> Optional[Column]:
        Column = util.preloaded.sql_column.Column
        ColumnProxy = util.preloaded.sql_column.ColumnProxy
        for obj in cls.__dict__.values():
            if isinstance(obj, Column | ColumnProxy) and obj.is_primary_key:
                return obj
        return None

    @util.preload_module("ormlambda.sql")
    @classmethod
    def get_columns(cls) -> tuple[Column, ...]:
        Column = util.preloaded.sql_column.Column

        return tuple([x for x in cls.__annotations__.values() if isinstance(x, Column)])

    @classmethod
    def get_column[TProp](cls, name: str) -> Column[TProp]:
        for key, value in cls.__annotations__.items():
            if name == key:
                return value

    @classmethod
    def create_table(cls, dialect: Dialect) -> str:
        return CreateTable(cls).compile(dialect).string

    @classmethod
    def drop_table(cls, dialect: Dialect) -> str:
        return DropTable(cls).compile(dialect).string

    def __eq__(self, __value: Any) -> bool:
        return hash(self) == hash(__value)

    def __hash__(self):
        return hash((self.__table_name__, *list(self.to_dict().items())))

    @classmethod
    def table_alias(cls, column: Optional[str] = None) -> str:
        if column:
            return f"`{cls.__table_name__}_{column}`"
        return cls.__table_name__

    @util.preload_module("ormlambda.sql")
    @classmethod
    def foreign_keys(cls) -> dict[str, ForeignKey]:
        ForeignKey = util.preloaded.sql_foreign_key.ForeignKey

        return {key: value for key, value in cls.__dict__.items() if isinstance(value, ForeignKey)}
