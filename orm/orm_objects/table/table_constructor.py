import base64
import datetime
from decimal import Decimal
from typing import Any, Iterable, Type, dataclass_transform
import json
from .column import Column

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
        return f"self._{self.name} = {self.default.__to_string__(self.name,self.name)}"


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
        default = getattr(cls, name, MISSING)
        fields.append(Field(name, field_type, default))

        # Update __annotations__ to create Columns
        cls.__annotations__[name] = Column[field_type]
    return fields


@dataclass_transform()
def __init_constructor__[T](cls: Type[T]) -> Type[T]:
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


def __create_properties[T](cls: Type[T], field: Field) -> property:
    _name: str = f"_{field.name}"
    type_ = field.type_
    # we need to get Table attributes (Column class) and then called __getattribute__ or __setattr__ to make changes inside of Column
    prop = property(
        fget=lambda self: __transform_getter(getattr(self, _name), type_),
        fset=lambda self, value: __transform_setter(getattr(self, _name), value, type_),
    )

    # set property in public name
    setattr(cls, field.name, prop)
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


@dataclass_transform()
class TableMeta(type):
    def __new__[T](cls: "Table", name: str, bases: tuple, dct: dict[str, Any]) -> Type[T]:
        cls_object = super().__new__(cls, name, bases, dct)
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
    __table_name__ = ...

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
                return value[:20]+ "..."
            return value

        dicc:dict[str,str] = {x:str(getattr(self,x)) for x in self.__annotations__}
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
