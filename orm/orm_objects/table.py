import json
from typing import Any, dataclass_transform
from .table_constructor.table_constructor import __init_constructor__

@dataclass_transform()
class TableMeta(type):
    def __new__(cls, name: str, bases: tuple, dct: dict[str, Any]):
        cls_object = super().__new__(cls, name, bases, dct)
        return __init_constructor__(cls_object)


@dataclass_transform(eq_default=False)
class Table(metaclass=TableMeta):
    __table_name__ = ...

    def __repr__(self) -> str:
        params = ", ".join([f"{x}={getattr(self,x)}" for x, y in self.__class__.__dict__.items() if isinstance(y, property)])
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        params = {x: getattr(self, x) for x, y in self.__class__.__dict__.items() if isinstance(y, property)}
        return json.dumps(params, ensure_ascii=False, indent=2)
