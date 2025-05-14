import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import create_engine, Table, Column
from ormlambda.sql.ddl import CreateTable
from ormlambda.dialects.mysql.types import INTEGER, VARCHAR


class Address(Table):
    __table_name__ = "address"

    address_id: int = Column(INTEGER(), is_primary_key=True)
    address: str = Column(VARCHAR(100))
    address2: str = Column(VARCHAR(100))
    district: str = Column(VARCHAR(100))
    city_id: int = Column(INTEGER())
    postal_code: str = Column(VARCHAR(100))
    phone: str = Column(VARCHAR(100))
    location: int = Column(bytes)


mysql = create_engine("mysql+mysqlconnector://root:1500@localhost:3306/sakila")
sqlite = create_engine("sqlite:///~/Downloads/sakila.db")


result = CreateTable(Address).compile(mysql)
result = CreateTable(Address).compile(sqlite)
pass
