from collections import defaultdict
from typing import Any, Callable, Iterable, Literal, Self, Type, dataclass_transform
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
            __create_properties(cls, field.name)

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


def __create_properties[T](cls: Type[T], prop_name: str) -> property:
    _name: str = f"_{prop_name}"

    # we need to get Table attributes (Column class) and then called __getattribute__ or __setattr__ to make changes inside of Column
    prop = property(
        fget=lambda _obj: getattr(_obj, _name).__getattribute__("column_value"),
        fset=lambda _obj, value: getattr(_obj, _name).__setattr__("column_value", value),
    )

    # set property in public name
    setattr(cls, prop_name, prop)
    return None


@dataclass_transform()
class TableMeta(type):
    def __new__[T](cls, name: str, bases: tuple, dct: dict[str, Any]) -> Type[T]:
        cls_object = super().__new__(cls, name, bases, dct)

        self = __init_constructor__(cls_object)
        self.query: dict[OrderQuery, list[str]] = defaultdict(list)
        return self


OrderQuery = Literal["select", "join", "where", "sort"]


@dataclass_transform(eq_default=False)
class Table(metaclass=TableMeta):
    __table_name__ = ...
    __order__ = ("select", "join", "where", "order")

    def __repr__(self) -> str:
        params = ", ".join([f"{x}={getattr(self,x)}" for x, y in self.__class__.__dict__.items() if isinstance(y, property)])
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        params = {x: getattr(self, x) for x, y in self.__class__.__dict__.items() if isinstance(y, property)}
        return json.dumps(params, ensure_ascii=False, indent=2)

    def __getattr__[T](self, __name: str) -> Column[T]:
        return self.__dict__.get(__name)

    def __init__(self):
        self.query: dict[OrderQuery, list[str]]

    # region public methods
    def join[TRight](
        self,
        table_right: TRight,
        table_left:Self=None,
        *,
        by: str,
        where: Callable[[Self, TRight], bool],
    ) -> Self:
        from orm.orm_objects.queries.joins import JoinSelector, JoinType

        if table_left is not None:
            self = table_left
        join_query = JoinSelector[Self, TRight](self, table_right, JoinType(by), where=where).query
        self.query["join"].append(join_query)
        return self

    def where[T](
        self,

        table: T,
        lambda_function: Callable[[T], bool],
    ) -> T:
        from orm.orm_objects.queries.where_condition import WhereCondition

        where_query = WhereCondition[T, None](table, None, lambda_function).to_query()
        self.query["where"].append(where_query)
        return self

    def select[T:Table](
        self,
        table:T,
        selector: Callable[[T], None],
    ) -> str:
        from orm.orm_objects.queries.select import SelectQuery

        select_query = SelectQuery[T](table, select_list=selector).query
        table.query["select"].append(select_query)

        res: str = ""
        for x in table.__order__:
            if query := table.query.get(x, None):
                res += "\n"
                res += "\n".join([x for x in query])
        return res

    # endregion
