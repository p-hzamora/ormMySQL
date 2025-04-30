"""
String Data Types
Data type	Description
CHAR(size)	A FIXED length string (can contain letters, numbers, and special characters). The size parameter specifies the column length in characters - can be from 0 to 255. Default is 1
VARCHAR(size)	A VARIABLE length string (can contain letters, numbers, and special characters). The size parameter specifies the maximum column length in characters - can be from 0 to 65535
BINARY(size)	Equal to CHAR(), but stores binary byte strings. The size parameter specifies the column length in bytes. Default is 1
VARBINARY(size)	Equal to VARCHAR(), but stores binary byte strings. The size parameter specifies the maximum column length in bytes.
TINYBLOB	For BLOBs (Binary Large OBjects). Max length: 255 bytes
TINYTEXT	Holds a string with a maximum length of 255 characters
TEXT(size)	Holds a string with a maximum length of 65,535 bytes
BLOB(size)	For BLOBs (Binary Large OBjects). Holds up to 65,535 bytes of data
MEDIUMTEXT	Holds a string with a maximum length of 16,777,215 characters
MEDIUMBLOB	For BLOBs (Binary Large OBjects). Holds up to 16,777,215 bytes of data
LONGTEXT	Holds a string with a maximum length of 4,294,967,295 characters
LONGBLOB	For BLOBs (Binary Large OBjects). Holds up to 4,294,967,295 bytes of data
ENUM(val1, val2, val3, ...)	A string object that can have only one value, chosen from a list of possible values. You can list up to 65535 values in an ENUM list. If a value is inserted that is not in the list, a blank value will be inserted. The values are sorted in the order you enter them
SET(val1, val2, val3, ...)	A string object that can have 0 or more values, chosen from a list of possible values. You can list up to 64 values in a SET list



Numeric Data Types
Data type	Description
BIT(size)	A bit-value type. The number of bits per value is specified in size. The size parameter can hold a value from 1 to 64. The default value for size is 1.
TINYINT(size)	A very small integer. Signed range is from -128 to 127. Unsigned range is from 0 to 255. The size parameter specifies the maximum display width (which is 255)
BOOL	Zero is considered as false, nonzero values are considered as true.
BOOLEAN	Equal to BOOL
SMALLINT(size)	A small integer. Signed range is from -32768 to 32767. Unsigned range is from 0 to 65535. The size parameter specifies the maximum display width (which is 255)
MEDIUMINT(size)	A medium integer. Signed range is from -8388608 to 8388607. Unsigned range is from 0 to 16777215. The size parameter specifies the maximum display width (which is 255)
INT(size)	A medium integer. Signed range is from -2147483648 to 2147483647. Unsigned range is from 0 to 4294967295. The size parameter specifies the maximum display width (which is 255)
INTEGER(size)	Equal to INT(size)
BIGINT(size)	A large integer. Signed range is from -9223372036854775808 to 9223372036854775807. Unsigned range is from 0 to 18446744073709551615. The size parameter specifies the maximum display width (which is 255)
FLOAT(size, d)	A floating point number. The total number of digits is specified in size. The number of digits after the decimal point is specified in the d parameter. This syntax is deprecated in MySQL 8.0.17, and it will be removed in future MySQL versions
FLOAT(p)	A floating point number. MySQL uses the p value to determine whether to use FLOAT or DOUBLE for the resulting data type. If p is from 0 to 24, the data type becomes FLOAT(). If p is from 25 to 53, the data type becomes DOUBLE()
DOUBLE(size, d)	A normal-size floating point number. The total number of digits is specified in size. The number of digits after the decimal point is specified in the d parameter
DOUBLE PRECISION(size, d)
DECIMAL(size, d)	An exact fixed-point number. The total number of digits is specified in size. The number of digits after the decimal point is specified in the d parameter. The maximum number for size is 65. The maximum number for d is 30. The default value for size is 10. The default value for d is 0.
DEC(size, d)	Equal to DECIMAL(size,d)
Note: All the numeric data types may have an extra option: UNSIGNED or ZEROFILL. If you add the UNSIGNED option, MySQL disallows negative values for the column. If you add the ZEROFILL option, MySQL automatically also adds the UNSIGNED attribute to the column.

Date and Time Data Types
Data type	Description
DATE	A date. Format: YYYY-MM-DD. The supported range is from '1000-01-01' to '9999-12-31'
DATETIME(fsp)	A date and time combination. Format: YYYY-MM-DD hh:mm:ss. The supported range is from '1000-01-01 00:00:00' to '9999-12-31 23:59:59'. Adding DEFAULT and ON UPDATE in the column definition to get automatic initialization and updating to the current date and time
TIMESTAMP(fsp)	A timestamp. TIMESTAMP values are stored as the number of seconds since the Unix epoch ('1970-01-01 00:00:00' UTC). Format: YYYY-MM-DD hh:mm:ss. The supported range is from '1970-01-01 00:00:01' UTC to '2038-01-09 03:14:07' UTC. Automatic initialization and updating to the current date and time can be specified using DEFAULT CURRENT_TIMESTAMP and ON UPDATE CURRENT_TIMESTAMP in the column definition
TIME(fsp)	A time. Format: hh:mm:ss. The supported range is from '-838:59:59' to '838:59:59'
YEAR	A year in four-digit format. Values allowed in four-digit format: 1901 to 2155, and 0000.
MySQL 8.0 does not support year in two-digit format.
"""

from ormlambda.types import DatabaseType
from ...factory.sql_type_factory import SQLTypeRenderer, SQLTypeRendererFactory
from ...sql_types import (
    Integer,
    String,
    Char,
    Text,
    Timestamp,
    DateTime,
    Boolean,
    point,
    Binary,
)


class MySQLIntegerRenderer(SQLTypeRenderer):
    """MySQL renderer for Integer type"""

    def render(self, sql_type: Integer) -> str:
        # MySQL uses INT for standard integer type
        return f"INT{' AUTO_INCREMENT' if sql_type.autoincrement else ''}"


class MySQLStringRenderer(SQLTypeRenderer):
    """MySQL renderer for String type"""

    def render(self, sql_type: String) -> str:
        # MySQL has performance implications for different VARCHAR sizes
        if sql_type.length is None:
            return "VARCHAR(255)"  # Default
        elif sql_type.length > 65535:
            return "TEXT"  # VARCHAR too large
        else:
            return f"VARCHAR({sql_type.length})"


class MySQLCharRenderer(SQLTypeRenderer):
    """MySQL renderer for Char type"""

    def render(self, sql_type: Char) -> str:
        # MySQL CHAR has a maximum length of 255
        if sql_type.length > 255:
            return f"VARCHAR({sql_type.length})"
        return f"CHAR({sql_type.length})"


class MySQLTextRenderer(SQLTypeRenderer):
    """MySQL renderer for Text type"""

    def render(self, sql_type: Text) -> str:
        # MySQL has different TEXT sizes
        if sql_type.size == "tiny":
            return "TINYTEXT"  # Up to 255 bytes
        elif sql_type.size == "medium":
            return "MEDIUMTEXT"  # Up to 16MB
        elif sql_type.size == "long":
            return "LONGTEXT"  # Up to 4GB
        return "TEXT"  # Up to 65KB


class MySQLTimestampRenderer(SQLTypeRenderer):
    """MySQL renderer for Timestamp type"""

    def render(self, sql_type: Timestamp) -> str:
        # MySQL TIMESTAMP has automatic properties and timezone handling
        # Precision is optional (fractional seconds)
        fsp = ""
        if sql_type.precision is not None:
            if 0 <= sql_type.precision <= 6:  # MySQL supports 0-6 fractional seconds
                fsp = f"({sql_type.precision})"

        # MySQL doesn't have special syntax for timezone in type definition
        # (timezone handling is a server/session setting)
        return f"TIMESTAMP{fsp}"


class MySQLDateTimeRenderer(SQLTypeRenderer):
    """MySQL renderer for DateTime type"""

    def render(self, sql_type: DateTime) -> str:
        # MySQL DATETIME can have precision for fractional seconds
        fsp = ""
        if sql_type.precision is not None:
            if 0 <= sql_type.precision <= 6:  # MySQL supports 0-6 fractional seconds
                fsp = f"({sql_type.precision})"
        return f"DATETIME{fsp}"


class MySQLBooleanRenderer(SQLTypeRenderer):
    """MySQL renderer for Boolean type"""

    def render(self, sql_type: Boolean) -> str:
        # MySQL BOOLEAN is just an alias for TINYINT(1)
        return "TINYINT(1)"


class MySQLPointRenderer(SQLTypeRenderer):
    """MySQL renderer for Point type"""

    def render(self, sql_type: point) -> str:
        """
        Render MySQL Point type

        MySQL spatial data requires the spatial extensions to be enabled.
        """
        # MySQL uses POINT type from spatial extension
        # SRID is typically set using ST_SRID() function rather than in the type declaration
        return "POINT"


class MySQLBinaryRenderer(SQLTypeRenderer):
    """MySQL renderer for Binary type"""

    def render(self, sql_type: Binary) -> str:
        # MySQL has different BINARY types based on size and fixed vs variable length
        if sql_type.length is None:
            # No length specified - use BLOB
            return "BLOB"
        elif sql_type.fixed_length:
            # Fixed length binary data
            if sql_type.length > 255:
                # BINARY limited to 255 bytes
                return "BLOB"
            return f"BINARY({sql_type.length})"
        else:
            # Variable length binary data
            if sql_type.length > 65535:
                # VARBINARY too large
                return "BLOB"
            return f"VARBINARY({sql_type.length})"


SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Integer", MySQLIntegerRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "String", MySQLStringRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Char", MySQLCharRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Text", MySQLTextRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Timestamp", MySQLTimestampRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "DateTime", MySQLDateTimeRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Boolean", MySQLBooleanRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Point", MySQLPointRenderer)
SQLTypeRendererFactory.register_renderer(DatabaseType.MYSQL, "Binary", MySQLBinaryRenderer)
