from .base_write import IWrite
from .base_read import IRead

from .int import MySQLCastInt

class MySQLCastFloat(IWrite[float]):
    @staticmethod
    def cast(value:float)->str:
        return MySQLCastInt.cast(value)
    
class MySQLReadFloat(IRead[float]):
    @staticmethod
    def cast(value:str)->float:
        return float(value)