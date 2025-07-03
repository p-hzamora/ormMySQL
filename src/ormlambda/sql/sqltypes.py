from __future__ import annotations
import decimal
import datetime as dt
import enum
import inspect
from types import NoneType
from typing import Literal, Optional, Any, Type, cast, get_args, overload
from .type_api import TypeEngine
import ormlambda.util as util
from uuid import UUID as _python_UUID
from shapely import Point as _python_Point


class _NoArg(enum.Enum):
    NO_ARG = 0

    def __repr__(self):
        return f"_NoArg.{self.name}"


NO_ARG = _NoArg.NO_ARG


# region Numeric Types
class Integer(TypeEngine[int]):
    """Standard integer type."""

    __visit_name__ = "integer"

    @property
    def python_type(self) -> Type[int]:
        return int

    def _resolve_for_literal_value(self, value: int) -> TypeEngine[int]:
        if value.bit_length() >= 32:
            return _BIGINTEGER
        return self


class SmallInteger(Integer):
    """Small-range integer."""

    __visit_name__ = "small_integer"


class BigInteger(Integer):
    """Large-range integer."""

    __visit_name__ = "big_integer"


type NumericType = float | decimal.Decimal


class NumericCommon[T: NumericType](TypeEngine[T]):
    """Exact numeric type with precision and scale."""

    def __init__(
        self,
        *,
        precision: Optional[int],
        scale: Optional[int],
        asdecimal: bool,
    ):
        self.precision = precision
        self.scale = scale
        self.asdecimal = asdecimal

    @property
    def python_type(self) -> Type[T]:
        if self.asdecimal:
            return decimal.Decimal
        return float


class Numeric[T: NumericType](NumericCommon[T]):
    __visit_name__ = "numeric"

    @overload
    def __init__(
        self: Numeric[float],
        precision: Optional[int] = ...,
        scale: Optional[int] = ...,
        asdecimal: Literal[False] = ...,
    ): ...
    @overload
    def __init__(
        self: Numeric[decimal.Decimal],
        precision: Optional[int] = ...,
        scale: Optional[int] = ...,
        asdecimal: Literal[True] = ...,
    ): ...
    def __init__(
        self,
        *,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
        asdecimal: bool = True,
    ):
        super().__init__(
            precision=precision,
            scale=scale,
            asdecimal=asdecimal,
        )


class Float[T: NumericType](NumericCommon[T]):
    """Floating point type."""

    __visit_name__ = "float"

    @overload
    def __init__(
        self: Numeric[float],
        precision: Optional[int] = ...,
        asdecimal: Literal[False] = ...,
    ): ...
    @overload
    def __init__(
        self: Numeric[decimal.Decimal],
        precision: Optional[int] = ...,
        asdecimal: Literal[True] = ...,
    ): ...
    def __init__(
        self,
        *,
        precision: Optional[int] = None,
        asdecimal: bool = False,
    ):
        super().__init__(
            precision=precision,
            scale=None,
            asdecimal=asdecimal,
        )


class Real[T: NumericType](Numeric[T]):
    """Real number type."""

    __visit_name__ = "real"


class Double[T: NumericType](Float[T]):
    """Double precision floating point."""

    __visit_name__ = "double"


# endregion


# region String Types
class String(TypeEngine[str]):
    """The base for all string and character types.

    In SQL, corresponds to VARCHAR.
    """

    __visit_name__ = "string"

    def __init__(
        self,
        length: Optional[int] = None,
        collation: Optional[str] = None,
    ):
        self.length = length
        self.collation = collation

    @property
    def python_type(self) -> Type[str]:
        return str

    def _resolve_for_literal_value(self, value: str) -> TypeEngine[str]:
        if value.isascii():
            return _STRING
        return _UNICODE


class Text(String):
    """Unbounded length text type."""

    __visit_name__ = "text"

    def __init__(
        self,
        length: Optional[int] = None,
        collation: Optional[str] = None,
    ):
        super().__init__(length, collation)


class Unicode(String):
    """Variable length Unicode string."""

    __visit_name__ = "unicode"

    def __init__(
        self,
        length: Optional[int] = None,
        collation: Optional[str] = None,
    ):
        super().__init__(length, collation)


class UnicodeText(String):
    """Unbounded length Unicode text."""

    __visit_name__ = "unicode_text"

    def __init__(
        self,
        length: Optional[int] = None,
        collation: Optional[str] = None,
    ):
        super().__init__(length, collation)


# endregion


# region Date and Time Types
class Date(TypeEngine[dt.date]):
    """Date type."""

    __visit_name__ = "date"

    @property
    def python_type(self) -> Type[dt.date]:
        return dt.date


class Time(TypeEngine[dt.time]):
    """Time type."""

    __visit_name__ = "time"

    def __init__(
        self,
        timezone: bool = False,
    ):
        self.timezone = timezone

    @property
    def python_type(self) -> Type[dt.time]:
        return dt.time

    def _resolve_for_literal_value(self, value: dt.datetime) -> TypeEngine[dt.datetime]:
        has_timezone = value.tzinfo is not None
        if has_timezone and not self.timezone:
            return TIME_TIMEZONE
        return self


class Datetime(TypeEngine[dt.datetime]):
    """Date and time type."""

    __visit_name__ = "datetime"

    def __init__(
        self,
        timezone: bool = False,
    ):
        self.timezone = timezone

    @property
    def python_type(self) -> Type[dt.datetime]:
        return dt.datetime

    def _resolve_for_literal_value(self, value: dt.datetime) -> TypeEngine[dt.datetime]:
        has_timezone = value.tzinfo is not None
        if has_timezone and not self.timezone:
            return DATETIME_TIMEZONE
        return self


class Timestamp(TypeEngine[int]):
    """Timestamp type with optional timezone support."""

    __visit_name__ = "timestamp"

    def __init__(
        self,
        timezone: bool = False,
        precision: Optional[int] = None,
    ):
        self.timezone = timezone
        self.precision = precision

    @property
    def python_type(self) -> Type[int]:
        return int


# endregion


# region Boolean Type
class Boolean(TypeEngine[bool]):
    """Boolean type."""

    __visit_name__ = "boolean"

    @property
    def python_type(self) -> Type[bool]:
        return bool


# endregion


# region Binary Types


class _Binary(TypeEngine[bytes]):
    """Define base behavior for binary types."""

    def __init__(self, length: Optional[int] = None):
        self.length = length


class LargeBinary(_Binary):
    """Binary data type."""

    __visit_name__ = "large_binary"

    @property
    def python_type(self) -> Type[bytes]:
        return bytes


class Varbinary(_Binary):
    """Variable-length binary data."""

    __visit_name__ = "varbinary"

    def __init__(
        self,
        length: Optional[int] = None,
    ):
        self.length = length


# endregion


# region Other Types
type EnumType = str | enum.Enum


class Enum(String, TypeEngine[EnumType]):
    """Enumerated type."""

    __visit_name__ = "enum"

    def __init__(
        self,
        *enums: str,
        name: Optional[str] = None,
        schema: Optional[str] = None,
    ):
        self.enums = enums
        self.name = name
        self.schema = schema

    @property
    def python_type(self) -> Type[EnumType]:
        if not self.enums:
            return super().python_type
        return enum.Enum

    def _resolve_for_literal_value(self, value: dt.datetime) -> TypeEngine[dt.datetime]:
        tv = type(value)
        type_ = self._resolve_for_literal_value(tv, tv, tv)
        assert type_ is not None
        return type_

    def _resolve_for_python_type(
        self,
        python_type: Type[Any],
        matched_on: Any,
        matched_on_flattened: Type[Any],
    ) -> Optional[Enum]:
        # "generic form" indicates we were placed in a type map
        # as ``sqlalchemy.Enum(enum.Enum)`` which indicates we need to
        # get enumerated values from the datatype
        we_are_generic_form = self._enums_argument == [enum.Enum]

        native_enum = None

        def process_literal(pt):
            # for a literal, where we need to get its contents, parse it out.
            enum_args = get_args(pt)
            bad_args = [arg for arg in enum_args if not isinstance(arg, str)]
            if bad_args:
                raise ValueError(f"Can't create string-based Enum datatype from non-string values: {', '.join(repr(x) for x in bad_args)}.  Please provide an explicit Enum datatype for this Python type")
            native_enum = False
            return enum_args, native_enum

        if not we_are_generic_form and python_type is matched_on:
            # if we have enumerated values, and the incoming python
            # type is exactly the one that matched in the type map,
            # then we use these enumerated values and dont try to parse
            # what's incoming
            enum_args = self._enums_argument

        elif util.is_literal(python_type):
            enum_args, native_enum = process_literal(python_type)
        elif util.is_pep695(python_type):
            value = python_type.__value__
            if not util.is_literal(value):
                raise ValueError(f"Can't associate TypeAliasType '{python_type}' to an Enum since it's not a direct alias of a Literal. Only aliases in this form `type my_alias = Literal['a', 'b']` are supported when generating Enums.")
            enum_args, native_enum = process_literal(value)

        elif isinstance(python_type, type) and issubclass(python_type, enum.Enum):
            # same for an enum.Enum
            enum_args = [python_type]

        else:
            enum_args = self._enums_argument

        # make a new Enum that looks like this one.
        # arguments or other rules
        kw = self._make_enum_kw({})

        if native_enum is False:
            kw["native_enum"] = False

        kw["length"] = NO_ARG if self.length == 0 else self.length
        return cast(
            Enum,
            self._generic_type_affinity(_enums=enum_args, **kw),  # type: ignore  # noqa: E501
        )

    def _setup_for_values(self, values, objects, kw):
        self.enums = list(values)

        self._valid_lookup = dict(zip(reversed(objects), reversed(values)))

        self._object_lookup = dict(zip(values, objects))

        self._valid_lookup.update([(value, self._valid_lookup[self._object_lookup[value]]) for value in values])


class Point(TypeEngine[_python_Point]):
    __visit_name__ = "point"

    @property
    def python_type(self) -> Type[_python_Point]:
        return _python_Point


class JSON(TypeEngine[Any]):
    """JSON data type."""

    __visit_name__ = "json"


type UuidType = str | _python_UUID


class UUID[T: UuidType](TypeEngine[UuidType]):
    """UUID type."""

    __visit_name__ = "UUID"

    @overload
    def __init__(self: UUID[_python_UUID], as_uuid: Literal[True] = ...): ...
    @overload
    def __init__(self: UUID[str], as_uuid: Literal[False] = ...): ...

    def __init__(self, as_uuid: bool = True):
        self.as_uuid = as_uuid

    @property
    def python_type(self) -> Type[UuidType]:
        return _python_UUID


# endregion


# region Basic datatypes


class NullType(TypeEngine[None]):
    __visit_name__ = "null"

    @property
    def python_type(self) -> NoneType:
        return NoneType


class INTEGER(Integer):
    __visit_name__ = "INTEGER"


INT = INTEGER


class SMALLINTEGER(SmallInteger):
    __visit_name__ = "SMALLINTEGER"


SMALLINT = SMALLINTEGER


class BIGINTEGER(BigInteger):
    __visit_name__ = "BIGINTEGER"


BIGINT = BIGINTEGER


class NUMERIC(Numeric):
    __visit_name__ = "NUMERIC"


class FLOAT(Float):
    __visit_name__ = "FLOAT"


class REAL(Real):
    __visit_name__ = "REAL"


class DOUBLE(Double):
    __visit_name__ = "DOUBLE"


class DECIMAL[T: NumericType](Numeric[T]):
    __visit_name__ = "DECIMAL"


class STRING(String):
    __visit_name__ = "STRING"


class TEXT(Text):
    __visit_name__ = "TEXT"


class UNICODE(Unicode):
    __visit_name__ = "UNICODE"


class UNICODETEXT(UnicodeText):
    __visit_name__ = "UNICODETEXT"


class CHAR(String):
    __visit_name__ = "CHAR"


class NCHAR(String):
    __visit_name__ = "NCHAR"


class BLOB(LargeBinary):
    """The SQL BLOB type"""

    __visit_name__ = "BLOB"


class BINARY(_Binary):
    """The SQL BINARY type."""

    __visit_name__ = "BINARY"


class VARCHAR(String):
    __visit_name__ = "VARCHAR"


class NVARCHAR(String):
    __visit_name__ = "NVARCHAR"


class DATE(Date):
    __visit_name__ = "DATE"


class TIME(Time):
    __visit_name__ = "TIME"


class DATETIME(Datetime):
    __visit_name__ = "DATETIME"


class TIMESTAMP(Timestamp):
    __visit_name__ = "TIMESTAMP"


class BOOLEAN(Boolean):
    __visit_name__ = "BOOLEAN"


class LARGEBINARY(LargeBinary):
    __visit_name__ = "LARGEBINARY"


class VARBINARY(Varbinary):
    __visit_name__ = "VARBINARY"


class ENUM(Enum):
    __visit_name__ = "ENUM"


class POINT(Point):
    __visit_name__ = "POINT"


NULLTYPE = NullType()
BOOLEANTYPE = Boolean()
STRINGTYPE = String()
INTEGERTYPE = Integer()
NUMERICTYPE: Numeric[decimal.Decimal] = Numeric()
DATETIME_TIMEZONE = Datetime(timezone=True)
TIME_TIMEZONE = TIME(timezone=True)

_BIGINTEGER = BigInteger()
_DATETIME = Datetime()
_TIME = Time()
_STRING = String(255, None)
_UNICODE = Unicode()
_BINARY = LargeBinary()
_ENUM = Enum(enum.Enum)

_type_dicc: dict[Any, TypeEngine[Any]] = {
    str: _STRING,
    int: Integer(),
    float: Float(),
    NoneType: NULLTYPE,
    dt.datetime: Datetime(timezone=False),
    dt.date: DATE(),
    bytes: _BINARY,
    bytearray: _BINARY,
    bool: Boolean(),
    enum.Enum: _ENUM,
    Literal: _ENUM,
    _python_UUID: UUID(),
    _python_Point: POINT(),
    decimal.Decimal: DECIMAL(),
}
# enderegion


def resolve_primitive_types[T](value: T) -> TypeEngine[T]:
    if inspect.isclass(value):
        type_ = _type_dicc.get(value, None)

        if type_:
            return type_

    _result_type = _type_dicc.get(type(value), None)
    if not _result_type:
        return NULLTYPE
    return _result_type._resolve_for_literal_value(value)
