from __future__ import annotations
import decimal
from typing import Literal, Optional, overload
from .type_api import TypeEngine

type type_N = decimal.Decimal | float


class NumericCommon[_N: type_N]:
    """common mixin for the :class:`.Numeric` and :class:`.Float` types.
    .. versionadded:: 2.1

    """

    _default_decimal_return_scale = 10

    def __init__(
        self,
        *,
        precision: Optional[int],
        scale: Optional[int],
        decimal_return_scale: Optional[int],
        asdecimal: bool,
    ):
        self.precision = precision
        self.scale = scale
        self.decimal_return_scale = decimal_return_scale
        self.asdecimal = asdecimal

    @property
    def _effective_decimal_return_scale(self):
        if self.decimal_return_scale is not None:
            return self.decimal_return_scale
        elif getattr(self, "scale", None) is not None:
            return self.scale
        else:
            return self._default_decimal_return_scale

    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER

    def literal_processor(self, dialect):
        def process(value):
            return str(value)

        return process

    @property
    def python_type(self):
        if self.asdecimal:
            return decimal.Decimal
        else:
            return float


class Numeric[T: type_N](NumericCommon[T], TypeEngine[T]):
    __visit_name__ = "numeric"

    @overload
    def __init__(
        self: Numeric[decimal.Decimal],
        precision: Optional[int] = ...,
        scale: Optional[int] = ...,
        decimal_return_scale: Optional[int] = ...,
        asdecimal: Literal[True] = ...,
    ): ...

    @overload
    def __init__(
        self: Numeric[float],
        precision: Optional[int] = ...,
        scale: Optional[int] = ...,
        decimal_return_scale: Optional[int] = ...,
        asdecimal: Literal[False] = ...,
    ): ...

    def __init__(
        self,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
        decimal_return_scale: Optional[int] = None,
        asdecimal: bool = True,
    ):
        super().__init__(
            precision=precision,
            scale=scale,
            decimal_return_scale=decimal_return_scale,
            asdecimal=asdecimal,
        )

    @property
    def _type_affinity(self):
        return Numeric


class INTEGER(TypeEngine):
    """
    Integer type for SQLAlchemy.
    """

    __visit_name__ = "integer"


class STRING(TypeEngine):
    """
    Integer type for SQLAlchemy.
    """

    __visit_name__ = "string"

    def __init__(
        self,
        length: Optional[int] = None,
        collation: Optional[str] = None,
    ):
        self.length = length
        self.collation = collation


class VARCHAR(STRING):
    """The SQL VARCHAR type."""

    __visit_name__ = "VARCHAR"


class CHAR(STRING):
    """The SQL CHAR type."""

    __visit_name__ = "CHAR"
