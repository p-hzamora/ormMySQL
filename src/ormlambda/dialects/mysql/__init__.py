from . import base
from . import mysqlconnector

from .types import (  # noqa: F401
    NUMERIC,
    DECIMAL,
    DOUBLE,
    REAL,
    FLOAT,
    INTEGER,
    BIGINT,
    MEDIUMINT,
    TINYINT,
    SMALLINT,
    BIT,
    TIME,
    TIMESTAMP,
    DATETIME,
    YEAR,
    TEXT,
    TINYTEXT,
    MEDIUMTEXT,
    LONGTEXT,
    VARCHAR,
    CHAR,
    NVARCHAR,
    NCHAR,
    TINYBLOB,
    MEDIUMBLOB,
    LONGBLOB,
)


from .repository import MySQLRepository  # noqa: F401
from .caster import MySQLCaster  # noqa: F401

# default dialect
base.dialect = dialect = mysqlconnector.dialect
