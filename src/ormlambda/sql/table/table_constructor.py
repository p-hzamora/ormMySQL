from __future__ import annotations
from decimal import Decimal
from typing import Any, Optional, Type, dataclass_transform
import base64
import datetime
import json

import shapely as sph


from ormlambda.sql import Column
from ormlambda.sql import ForeignKey
from ormlambda.sql.dtypes import get_query_clausule
from .fields import get_fields
from ormlambda.utils.module_tree.dfs_traversal import DFSTraversal


@dataclass_transform()
def __init_constructor__[T](cls: Type[T]) -> Type[T]:
    fields = get_fields(cls)

    locals_: dict[str, Any] = {}
    init_args: list[str] = ["self"]
    assignments: list[str] = []

    for field in fields:
        if field.name.startswith("__"):
            continue

        locals_[field.type_name] = field.type_
        locals_[field.default_name] = None

        init_args.append(field.init_arg)
        assignments.append(field.assginment)

    string_locals_ = ", ".join(locals_)
    string_init_args = ", ".join(init_args)
    string_assignments = "".join([f"\n\t\t{x}" for x in assignments])

    wrapper_fn = "\n".join(
        [
            f"def wrapper({string_locals_}):",
            f"\n\tdef __init__({string_init_args}):",
            string_assignments,
            "\treturn __init__",
        ]
    )

    namespace = {}

    exec(wrapper_fn, None, namespace)
    init_fn = namespace["wrapper"](**locals_)

    setattr(cls, "__init__", init_fn)
    return cls


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
        return f'{self.__class__.__name__}({", ".join(equal_loop)})'

    def __getitem__[TProp](self, value: str | Column[TProp]) -> Optional[TProp]:
        name = value if isinstance(value, str) else value.column_name
        if hasattr(self, name):
            return getattr(self, name)
        return None

    def to_dict(self) -> dict[str, str | int]:
        dicc: dict[str, Any] = {}
        for x in self.__annotations__:
            transform_data = self.__transform_data__(getattr(self, x))
            dicc[x] = transform_data
        return dicc

    @staticmethod
    def __transform_data__[T](_value: T) -> T:
        def byte_to_string(value: bytes):
            return base64.b64encode(value).decode("utf-8")

        transform_map: dict = {
            datetime.datetime: datetime.datetime.isoformat,
            datetime.date: datetime.date.isoformat,
            Decimal: str,
            bytes: byte_to_string,
            set: list,
            sph.Point: lambda x: sph.to_wkt(x, rounding_precision=-1),
        }

        if (dtype := type(_value)) in transform_map:
            return transform_map[dtype](_value)
        return _value

    @classmethod
    def get_pk(cls) -> Optional[Column]:
        for obj in cls.__dict__.values():
            if isinstance(obj, Column) and obj.is_primary_key:
                return obj
        return None

    @classmethod
    def get_columns(cls) -> tuple[str, ...]:
        return tuple([x for x in cls.__annotations__.values() if isinstance(x, Column)])

    @classmethod
    def get_column[TProp](cls,name:str) -> Column[TProp]:
        for key,value in cls.__annotations__.items():
            if name == key:
                return value

    @classmethod
    def create_table_query(cls) -> str:
        """It's classmethod because of it does not matter the columns values to create the table"""
        all_clauses: list[str] = []

        all_clauses.extend(cls._create_sql_column_query())
        all_clauses.extend(ForeignKey.create_query(cls))

        return f"CREATE TABLE {cls.__table_name__} ({', '.join(all_clauses)});"

    @classmethod
    def _create_sql_column_query(cls) -> list[str]:
        """
        It's imperative to instantiate cls() to initialize the 'Table' object and create private variables that will be Column objects.
        Otherwise, we only can access to property method
        """
        annotations: dict[str, Column] = cls.__annotations__
        all_columns: list = []
        for col_obj in annotations.values():
            all_columns.append(get_query_clausule(col_obj))
        return all_columns

    @classmethod
    def find_dependent_tables(cls) -> tuple["Table", ...]:
        """Work in progress"""
        return

        # TODOL: Dive into new way to return dependent tables
        def get_involved_tables(graph: dict[Table, list[Table]], table_name: str) -> None:
            """
            Create a graph to be ordered
            """
            table = ForeignKey[Table, Table].MAPPED[table_name]
            for x in table.referenced_tables:
                if data := ForeignKey.MAPPED.get(x, None):
                    get_involved_tables(graph, data.table_object.__table_name__)

            graph[table.table_object.__table_name__] = list(table.referenced_tables)
            return None

        graph: dict[Table, list[Table]] = {}
        dependent = ForeignKey.MAPPED.get(cls.__table_name__, None)
        if dependent is None:
            return tuple([])

        graph[cls.__table_name__] = list(dependent.referenced_tables)
        get_involved_tables(graph, cls.__table_name__)

        dfs = DFSTraversal.sort(graph)

        order_table = dfs[: dfs.index(cls.__table_name__)]

        return [ForeignKey.MAPPED[x].table_object for x in order_table]

    def __eq__(self, __value: Any) -> bool:
        if isinstance(__value, Table):
            return all(
                (
                    self.__table_name__ == __value.__table_name__,
                    tuple(self.to_dict().items()),
                )
            )
        return False

    @classmethod
    def table_alias(cls, column: Optional[str] = None) -> str:
        if column:
            return f"`{cls.__table_name__}_{column}`"
        return cls.__table_name__

    @classmethod
    def foreign_keys(cls) -> dict[str, ForeignKey]:
        return {key: value for key, value in cls.__dict__.items() if isinstance(value, ForeignKey)}
