from datetime import datetime

import dbcontext as db
from orm import Table, Column, ForeignKey

from orm import MySQLRepository, IRepositoryBase

from orm.model_base import ModelBase
from test.models import (  # noqa: E402
    AddressModel,
    # City,
    # CityModel,
    # Address,
    # Actor,
    # ActorModel,
    # Country,
    # CountryModel,
)

from dotenv import load_dotenv

load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


class A(Table):
    __table_name__ = "a"
    pk_a: int = Column(is_primary_key=True)
    name_a: str
    data_a: str
    date_a: datetime


class B(Table):
    __table_name__ = "b"
    pk_b: int = Column(is_primary_key=True)
    data_b: str
    fk_a: int

    a = ForeignKey["B", A](__table_name__, A, lambda b, a: b.fk_a == a.pk_a)


class C(Table):
    __table_name__ = "c"
    pk_c: int = Column(is_primary_key=True)
    data_c: str
    fk_b: int
    b = ForeignKey["C", B](__table_name__, B, lambda c, b: c.fk_b == b.pk_b)


class D(Table):
    __table_name__ = "d"
    pk_d: int = Column(is_primary_key=True)
    data_d: str
    fk_c: int
    c = ForeignKey["D", C](__table_name__, C, lambda d, c: d.fk_c == c.pk_c)


class DModel(ModelBase[D]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(D, repository=repository)


# a = A(1, "pablo", "trabajador", datetime.now())
# b = B(2, "data_b", 1)
# c = C(3, "data_c", 2)
d = D(4, "data_d", 3)

database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()


d_instance = d
ad_filter = (
    DModel(database)
    .where(d_instance, lambda d: d.pk_d == 4)
    .select(
        lambda d: (
            d.c.b,
            d.data_d,
            d.c.data_c,
            d.c.b.data_b,
            d.c.b.a.data_a,
        )
    )
)


print(ad_filter)


# db_common = MySQLRepository(user=USERNAME, password=PASSWORD, database="common", host=HOST).connect()


address = db.Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())

a_model = AddressModel(database)

filtro = a_model.where(address, lambda a: a.address_id == 1).select(lambda a:( a, a.city, a.city.country))
