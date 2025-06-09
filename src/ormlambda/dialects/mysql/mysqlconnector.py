# dialects/mysql/mysqlconnector.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

r"""
.. dialect:: mysql+mysqlconnector
    :name: MySQL Connector/Python
    :dbapi: myconnpy
    :connectstring: mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
    :url: https://pypi.org/project/mysql-connector-python/

.. note::

    The MySQL Connector/Python DBAPI has had many issues since its release,
    some of which may remain unresolved, and the mysqlconnector dialect is
    The recommended MySQL dialects are mysqlclient and PyMySQL.

"""  # noqa

from __future__ import annotations
from types import ModuleType
from .base import MySQLCompiler
from .base import MySQLDialect


class MySQLCompiler_mysqlconnector(MySQLCompiler):
    def visit_mod_binary(self, binary, operator, **kw):
        return self.process(binary.left, **kw) + " % " + self.process(binary.right, **kw)


class MySQLDialect_mysqlconnector(MySQLDialect):
    driver = "mysqlconnector"
    statement_compiler = MySQLCompiler_mysqlconnector

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from mysql import connector

        return connector


dialect = MySQLDialect_mysqlconnector
