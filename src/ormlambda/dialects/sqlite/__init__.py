from . import base
from . import pysqlite

# default dialect
base.dialect = dialect = pysqlite.dialect
