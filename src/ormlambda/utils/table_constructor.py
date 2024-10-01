import base64
import datetime
from decimal import Decimal
from typing import Any, Iterable, Optional, Type, dataclass_transform
import json

from .dtypes import get_query_clausule
from .module_tree.dfs_traversal import DFSTraversal
from .column import Column

from .foreign_key import ForeignKey, TableInfo

MISSING = Column()


class Field:
    def __init__(self, name: str, type_: type, default: object) -> None:
        self.name: str = name
        self.type_: type = type_
        self.default: Column = default

    def __repr__(self) -> str:
        return f"{Field.__name__}(name = {self.name}, type_ = {self.type_}, default = {self.default})"

    @property
    def has_default(self) -> bool:
        return self.default is not MISSING

    @property
    def init_arg(self) -> str:
        # default = f"={self.default_name if self.has_default else None}"
        default = f"={None}"

        return f"{self.name}: {self.type_name}{default}"

    @property
    def default_name(self) -> str:
        return f"_dflt_{self.name}"

    @property
    def type_name(self) -> str:
        return f"_type_{self.name}"

    @property
    def assginment(self) -> str:
        return f"self._{self.name} = {self.default.__to_string__(self.name,self.name,self.type_name)}"


def delete_special_variables(dicc: dict[str, object]) -> None:
    keys = tuple(dicc.keys())
    for key in keys:
        if key.startswith("__"):
            del dicc[key]


def get_fields[T](cls: Type[T]) -> Iterable[Field]:
    annotations = getattr(cls, "__annotations__", {})

    # delete_special_variables(annotations)
    fields = []
    for name, type_ in annotations.items():
        # type_ must by Column object
        field_type = type_
        if hasattr(type_, "__origin__") and type_.__origin__ is Column:  # __origin__ to get type of Generic value
            field_type = type_.__args__[0]
        default: Column = getattr(cls, name, MISSING)
        fields.append(Field(name, field_type, default))

        # Update __annotations__ to create Columns
        cls.__annotations__[name] = Column[field_type]
    return fields


@dataclass_transform()
def __init_constructor__[T](cls: Type[T]) -> Type[T]:
    # create '__properties_mapped__' dictionary for each Table to avoid shared information
    # TODOL: I don't know if it's better to create a global dictionary like in commit '7de69443d7a8e7264b8d5d604c95da0e5d7e9cc0'
    setattr(cls, "__properties_mapped__", {})
    fields = get_fields(cls)
    locals_ = {}
    init_args = []

    for field in fields:
        if not field.name.startswith("__"):
            locals_[field.type_name] = field.type_

            init_args.append(field.init_arg)
            locals_[field.default_name] = None  # field.default.column_value
            __create_properties(cls, field)

    wrapper_fn = "\n".join(
        [
            f"def wrapper({', '.join(locals_.keys())}):",
            f" def __init__(self, {', '.join(init_args)}):",
            "\n".join([f"  {f.assginment}" for f in fields]) or "  pass",
            " return __init__",
        ]
    )

    namespace = {}

    exec(wrapper_fn, None, namespace)
    init_fn = namespace["wrapper"](**locals_)

    setattr(cls, "__init__", init_fn)
    return cls


def __create_properties(cls: Type["Table"], field: Field) -> property:
    _name: str = f"_{field.name}"
    type_ = field.type_
    # we need to get Table attributes (Column class) and then called __getattribute__ or __setattr__ to make changes inside of Column
    prop = property(
        fget=lambda self: __transform_getter(getattr(self, _name), type_),
        fset=lambda self, value: __transform_setter(getattr(self, _name), value, type_),
    )

    # set property in public name
    setattr(cls, field.name, prop)
    cls.__properties_mapped__[prop] = field.name
    return None


def __transform_getter[T](obj: object, type_: T) -> T:
    return obj.__getattribute__("column_value")

    # if type_ is str and isinstance(eval(obj), Iterable):
    #     getter = eval(obj)
    # return getter


def __transform_setter[T](obj: object, value: Any, type_: T) -> None:
    return obj.__setattr__("column_value", value)

    # if type_ is list:
    #     setter = str(setter)
    # return None


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

        TableMeta.__add_to_ForeignKey(cls_object)
        self = __init_constructor__(cls_object)
        return self

    def __repr__(cls: "Table") -> str:
        return f"{TableMeta.__name__}: {cls.__table_name__}"

    @staticmethod
    def __add_to_ForeignKey(cls: "Table") -> None:
        """
        When creating a Table class, we cannot pass the class itself as a parameter in a function that initializes a class variable.
        To fix this, we first add the table name as key and then, we add the class itself in the TableInfo class.
        """
        if table_info := ForeignKey.MAPPED.get(cls.__table_name__, None):
            table_info.table_object = cls
        else:
            ForeignKey.MAPPED[cls.__table_name__] = TableInfo()
            ForeignKey.MAPPED[cls.__table_name__].table_object = cls

        return None


@dataclass_transform(eq_default=False)
class Table(metaclass=TableMeta):
    """
    Class to mapped database tables with Python classes.

    It uses __annotations__ special var to store all table columns. If you do not type class var it means this var is not store as table column
    and it do not going to appear when you instantiate the object itself.

    This principle it so powerful due to we can create Foreign Key references without break __init__ class method.

    >>> class Address(Table):
    >>>     __table_name__ = "address"

    >>>     address_id: int = Column[int](is_primary_key=True)
    >>>     address: str
    >>>     address2: str
    >>>     district: str
    >>>     city_id: int
    >>>     postal_code: datetime
    >>>     phone: str
    >>>     location: datetime
    >>>     last_update: datetime = Column[datetime](is_auto_generated=True)

    >>>     city = ForeignKey["Address", City](__table_name__, City, lambda a, c: a.city_id == c.city_id)
    """

    __table_name__: str = ...
    __properties_mapped__: dict[property, str] = ...

    def __str__(self) -> str:
        params = self.to_dict()
        return json.dumps(params, ensure_ascii=False, indent=2)

    def __getattr__[T](self, __name: str) -> Column[T]:
        return self.__dict__.get(__name, None)

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
        }

        if (dtype := type(_value)) in transform_map:
            return transform_map[dtype](_value)
        return _value

    def get_pk(self) -> Optional[Column]:
        for col_name in self.__annotations__.keys():
            private_col = f"_{col_name}"
            col_obj = getattr(self, private_col)
            if isinstance(col_obj, Column) and col_obj.is_primary_key:
                return col_obj
        return None

    @classmethod
    def get_columns(cls) -> tuple[str, ...]:
        return tuple(cls.__annotations__.keys())

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
        table_init_ = cls()
        annotations: dict[str, Column] = table_init_.__annotations__
        all_columns: list = []
        for col_name in annotations.keys():
            col_object: Column = getattr(table_init_, f"_{col_name}")
            all_columns.append(get_query_clausule(col_object))
        return all_columns

    @classmethod
    def find_dependent_tables(cls) -> tuple["Table", ...]:
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
