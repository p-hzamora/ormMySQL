# dialects/mysql/types.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


from ...sql import sqltypes


class _NumericCommonType:
    """Base for MySQL numeric types.

    This is the base both for NUMERIC as well as INTEGER, hence
    it's a mixin.

    """

    def __init__(self, unsigned=False, zerofill=False, **kw):
        self.unsigned = unsigned
        self.zerofill = zerofill
        super().__init__(**kw)


class _NumericType(_NumericCommonType, sqltypes.Numeric): ...


class _IntegerType(_NumericCommonType, sqltypes.INTEGER):
    def __init__(self, display_width=None, **kw):
        self.display_width = display_width
        super().__init__(**kw)


class _StringType(sqltypes.STRING):
    """Base for MySQL string types."""

    def __init__(
        self,
        charset=None,
        collation=None,
        ascii=False,  # noqa
        binary=False,
        unicode=False,
        national=False,
        **kw,
    ):
        self.charset = charset

        # allow collate= or collation=
        kw.setdefault("collation", kw.pop("collate", collation))

        self.ascii = ascii
        self.unicode = unicode
        self.binary = binary
        self.national = national
        super().__init__(**kw)


class INTEGER(_IntegerType, sqltypes.INTEGER):
    """MySQL INTEGER type."""

    __visit_name__ = "INTEGER"

    def __init__(self, display_width=None, **kw):
        """Construct an INTEGER.

        :param display_width: Optional, maximum display width for this number.

        :param unsigned: a boolean, optional.

        :param zerofill: Optional. If true, values will be stored as strings
          left-padded with zeros. Note that this does not effect the values
          returned by the underlying database API, which continue to be
          numeric.

        """
        super().__init__(display_width=display_width, **kw)


class VARCHAR(_StringType, sqltypes.VARCHAR):
    """MySQL VARCHAR type, for variable-length character data."""

    __visit_name__ = "VARCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a VARCHAR.

        :param charset: Optional, a column-level character set for this string
          value.  Takes precedence to 'ascii' or 'unicode' short-hand.

        :param collation: Optional, a column-level collation for this string
          value.  Takes precedence to 'binary' short-hand.

        :param ascii: Defaults to False: short-hand for the ``latin1``
          character set, generates ASCII in schema.

        :param unicode: Defaults to False: short-hand for the ``ucs2``
          character set, generates UNICODE in schema.

        :param national: Optional. If true, use the server's configured
          national character set.

        :param binary: Defaults to False: short-hand, pick the binary
          collation type that matches the column's character set.  Generates
          BINARY in schema.  This does not affect the type of data stored,
          only the collation of character data.

        """
        super().__init__(length=length, **kwargs)


class CHAR(_StringType, sqltypes.CHAR):
    """MySQL CHAR type, for fixed-length character data."""

    __visit_name__ = "CHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a CHAR.

        :param length: Maximum data length, in characters.

        :param binary: Optional, use the default binary collation for the
          national character set.  This does not affect the type of data
          stored, use a BINARY type for binary data.

        :param collation: Optional, request a particular collation.  Must be
          compatible with the national character set.

        """
        super().__init__(length=length, **kwargs)

    @classmethod
    def _adapt_string_for_cast(cls, type_):
        # copy the given string type into a CHAR
        # for the purposes of rendering a CAST expression
        type_ = sqltypes.to_instance(type_)
        if isinstance(type_, sqltypes.CHAR):
            return type_
        elif isinstance(type_, _StringType):
            return CHAR(
                length=type_.length,
                charset=type_.charset,
                collation=type_.collation,
                ascii=type_.ascii,
                binary=type_.binary,
                unicode=type_.unicode,
                national=False,  # not supported in CAST
            )
        else:
            return CHAR(length=type_.length)
