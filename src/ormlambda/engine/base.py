from ormlambda.dialects import Dialect
from ormlambda.engine import url


class Engine:
    def __init__(self, dialect: Dialect, url: url.URL):
        self.dialect = dialect
        self.url = url
