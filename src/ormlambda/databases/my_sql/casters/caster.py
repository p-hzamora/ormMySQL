from __future__ import annotations

from ormlambda.common.interfaces import ICaster

class MySQLCaster(ICaster):
    from .write import MySQLWriteCastBase
    from .read import MySQLReadCastBase

    WRITE = MySQLWriteCastBase()
    READ = MySQLReadCastBase()
