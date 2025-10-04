from __future__ import annotations
from datetime import datetime
import sys
from pathlib import Path
from typing import Any, Iterable, Optional, Type, cast
import json
import base64

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from pydantic import BaseModel
from test.config import create_sakila_engine
from ormlambda import ORM, Column
from test.models import Address


engine = create_sakila_engine()

type DataType = dict[str, Any]


class PageInfo(BaseModel):
    size: int
    prev: Optional[int] = None
    next: Optional[int] = None


class Meta(BaseModel):
    page: PageInfo


class BaseCursor(BaseModel):
    meta: Meta


class CursorResponse(BaseCursor): ...


class AddressResponse(BaseModel):
    address_id: int
    address: str
    address2: Optional[str]
    district: str
    city_id: int
    postal_code: str
    phone: str
    last_update: datetime


class DBCursor[T]:
    def __init__(self, data: CursorResponse):
        self.result = data

    def encode(self) -> str:
        json_string = self.result.model_dump_json()

        json_bytes = json_string.encode("utf-8")
        base64_bytes = base64.b64encode(json_bytes)

        return base64_bytes.decode("utf-8")

    def __repr__(self):
        return f"{DBCursor.__name__}: {self.result}"

    @classmethod
    def decode(cls: Type[DBCursor], cursor_string: str) -> DBCursor[T]:
        if not cursor_string:
            return None
        try:
            json_bytes = base64.b64decode(cursor_string)

            json_string = json_bytes.decode("utf-8")

            model = CursorResponse(**json.loads(json_string))
            return cls(model)
        except Exception as e:
            raise ValueError(f"Invalid cursor: {e}")


type FilteredCols = dict[str, Iterable[str]]


def paginated_response(
    cursor: Optional[str] = None,
    size: int = 10,
    columns: Optional[FilteredCols] = None,
) -> tuple[tuple[AddressResponse, ...], DBCursor]:
    def selected_columns(address: Address):
        return (
            address.address_id,
            address.address,
            address.address2,
            address.district,
            address.city_id,
            address.postal_code,
            address.phone,
            address.last_update,
        )

    db_cursor = DBCursor.decode(cursor)

    model = ORM(Address, engine)
    model.order(lambda x: x.address_id, "ASC")
    model.limit(size)

    if db_cursor and (next := db_cursor.result.meta.page.next):
        model.where(lambda x: x.address_id > next)

    if columns:
        for col, values in columns.items():
            val = "|".join(map(str, values))
            model.where(lambda x: cast(Column, getattr(x, col)).regex(f"{val}"), True)

    data = model.select(selected_columns, flavour=AddressResponse)

    cursor_response = CursorResponse(
        meta=Meta(
            page=PageInfo(
                size=size,
                prev=None if not db_cursor else db_cursor.result.meta.page.prev,
                next=None if not data else data[-1].address_id,
            )
        ),
    )

    return data, DBCursor(cursor_response).encode()


data, cursor = paginated_response(
    columns={
        "address_id": (1, 10, 20, 21, 22, 23, 24, 25, 100, 111),
        "address": ("1795", "360", "270"),
    }
)
data, cursor = paginated_response(cursor)


pass
