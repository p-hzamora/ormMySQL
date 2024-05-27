import json
from typing import Any, dataclass_transform
from .column import Column


class TableMeta(type):
    def __new__(cls, name: str, bases: tuple, dct: dict[str, Any]):
        annotations = dct.get("__annotations__", {})
        fields = list(annotations.keys())

        if "__init__" not in dct:

            def __init__(self, *args, **kwargs):
                for field, arg in zip(fields, args):
                    attr: Column = getattr(self, field)
                    attr.column_name = arg

                for field, value in kwargs.items():
                    attr: Column = getattr(self, field)
                    attr.column_name = value

            dct["__init__"] = __init__

        cls_object = super().__new__(cls, name, bases, dct)
        cls_object.__annotations__ = annotations
        return cls_object


@dataclass_transform(eq_default=False)
class Table(metaclass=TableMeta):
    __table_name__: str = ...

    def __repr__(self) -> str:
        params = ", ".join([f"{x}={getattr(self,x)}" for x, y in self.__class__.__dict__.items() if isinstance(y, property)])
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        params = {x: getattr(self, x) for x, y in self.__class__.__dict__.items() if isinstance(y, property)}
        return json.dumps(params, ensure_ascii=False, indent=2)
