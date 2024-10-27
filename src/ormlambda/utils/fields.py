import typing as tp
from .column import Column

__all__ = ["get_fields"]

MISSING = lambda: Column()  # COMMENT: Very Important to avoid reusing the same variable across different classes.  # noqa: E731


class Field[TProp: tp.AnnotatedAny]:
    def __init__(self, name: str, type_: tp.Type, default: Column[TProp]) -> None:
        self.name: str = name
        self.type_: tp.Type[TProp] = type_
        self.default: Column[TProp] = default

    def __repr__(self) -> str:
        return f"{Field.__name__}(name = {self.name}, type_ = {self.type_}, default = {self.default})"

    @property
    def has_default(self) -> bool:
        return self.default is not MISSING()

    @property
    def init_arg(self) -> str:
        default = f"={self.default_name}"  # if self.has_default else ""}"
        return f"{self.name}: {self.type_name}{default}"

    @property
    def default_name(self) -> str:
        return f"_dflt_{self.name}"

    @property
    def type_name(self) -> str:
        return f"_type_{self.name}"

    @property
    def assginment(self) -> str:
        return f"self._{self.name} = {self.default.__to_string__(self)}"


def get_fields[T, TProp](cls: tp.Type[T]) -> tp.Iterable[Field]:
    # COMMENT: Used the 'get_type_hints' method to resolve typing when 'from __future__ import annotations' is in use
    annotations = {key: val for key, val in tp.get_type_hints(cls).items() if not key.startswith("_")}

    # delete_special_variables(annotations)
    fields = []
    for name, type_ in annotations.items():
        if hasattr(type_, "__origin__") and type_.__origin__ is Column:  # __origin__ to get type of Generic value
            field_type = type_.__args__[0]
        else:
            # type_ must by Column object
            field_type: TProp = type_

        default: Column = getattr(cls, name, MISSING())

        default.dtype = field_type  # COMMENT: Useful for setting the dtype variable after instantiation.
        fields.append(Field[TProp](name, field_type, default))

        # Update __annotations__ to create Columns
        cls.__annotations__[name] = default
    return fields
