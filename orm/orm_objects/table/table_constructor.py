from typing import Iterable, Type, dataclass_transform

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
        default = f"={self.default_name}" if self.has_default else ""

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


def get_fields[T](cls: Type[T]) -> Iterable[Field]:
    annotations = getattr(cls, "__annotations__", {})

    fields = []
    for name, type_ in annotations.items():
        # type_ must by Column object
        if type_.__origin__ is not Column:
            raise Exception(f"'{type_}' is not {Column.__name__}")

        default = getattr(cls, name, MISSING)
        fields.append(Field(name, type_.__args__[0], default))

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
            if field.has_default:
                # set Column Object
                locals_[field.default_name] = field.default.__to_string__(field.name, field.name)

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

    setattr(
        cls,
        "age",
        property(fget=lambda self: self._age.column_value, fset=lambda self, value: self._age.__setattr__(self, "column_value", value)),
    )

    setattr(
        cls,
        "name",
        property(fget=lambda self: self._name.column_value, fset=lambda self, value: self._name.__setattr__(self, "column_value", value)),
    )

    # for field in fields:
    #      __create_properties(cls, field.name)

    return cls


# def __create_properties[T](cls: Type[T], pname: str) -> None:
#     if hasattr(cls, pname):
#         private_attr: Column[T] = setattr(cls, f"_{pname}",Column())
#         prop = property(
#             fget=lambda self: private_attr.column_value,
#             fset=lambda self, value: setattr(private_attr, "column_value", value),
#         )
#         # set property in public name
#         setattr(cls, pname, prop)
#     return None


@dataclass_transform()
class MetaBase(type):
    def __new__[T](cls: T, n, b, dct) -> Type[T]:
        cls_object = super().__new__(cls, n, b, dct)
        return __init_constructor__(cls_object)


class Base(metaclass=MetaBase): ...
