import sys
from pathlib import Path
from env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)
import math

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import ORM
from ormlambda.databases.my_sql.clauses.joins import JoinType  # noqa: E402
from models.staff import Staff  # noqa: E402
from models.address import Address  # noqa: E402
from models.actor import Actor  # noqa: E402
from models.store import Store  # noqa: E402


db = MySQLRepository(user=DB_USERNAME, password=DB_PASSWORD, database=DB_DATABASE, host=DB_HOST)

StaffModel = ORM(Staff, db)
AddressModel = ORM(Address, db)
ActorModel = ORM(Actor, db)
StoreModel = ORM(Store, db)


result = AddressModel.where(Address.City.Country.country_id == 87).select(
    lambda address: (
        address.city_id,
        address.City.city_id,
        address.City.country_id,
        address.City.Country.country_id,
    ),
    flavour=tuple,
)
res = AddressModel.where(Address.City.Country.country.regex(r"^[aA]")).select(
    lambda a: (
        a,
        a.City,
        a.City.Country,
    ),
    by=JoinType.INNER_JOIN,
    flavour=tuple,
)


query = Actor.create_table_query()

asdf = "TEST_DB"
StaffModel.repository.create_database(asdf, "replace")
StaffModel.repository.drop_database(asdf)


staff = StaffModel.where(Staff.staff_id == 1).select_one()
staff.staff_id = 100
StaffModel.upsert(staff)
id = StaffModel.order(lambda x: x.staff_id, order_type="DESC").where(Staff.staff_id == staff.staff_id).select_one().staff_id
new_staff = StaffModel.where(Staff.staff_id == id).select_one()
new_staff.first_name = "PEPON"
StaffModel.upsert(new_staff)

staffs = StaffModel.where(Staff.staff_id > 2).delete()


res_tuple_3 = (
    AddressModel.order(lambda a: a.address_id, order_type="DESC")
    .where(Address.City.Country.country_id == 87)
    .select(
        lambda a: (
            a,
            a.City,
            a.City.Country,
        )
    )
)

result = (
    AddressModel.order(lambda a: a.address_id, order_type="DESC")
    .where(Address.City.Country.country_id.regex(r"^[A]"))
    .limit(100)
    .select(
        lambda a: (
            a.address_id,
            a.City.city_id,
            a.City.Country.country_id,
            a.City.Country.country,
        ),
        flavour=dict,
    )
)


res_one_table_five_results = AddressModel.where(Address.address_id <= 5).limit(100).order(lambda a: a.address_id, order_type="DESC").select(lambda a: (a,))
res_one_table_one_result = AddressModel.where(Address.address_id == 5).order(lambda a: a.address_id, order_type="DESC").select_one()
res_one_table_one_result = AddressModel.where(Address.address2 == 100).order(lambda a: a.address_id, order_type="DESC").select_one(lambda x: x)


query = """
SELECT address.address_id as `kkk`, country.country as `country_country`, city.city as `city_city`, address.address as `address_address` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id
WHERE country.country REGEXP '^[FHA]' AND (city.city REGEXP '[^W]') AND (177 >= address.address_id) AND (address.address_id <= 28)
ORDER BY address.address_id DESC
"""
address = AddressModel.repository.read_sql(query, flavour=dict)
pass


def pagination(page: int):
    limit = 20
    total_register: int = AddressModel.repository.read_sql(f"SELECT COUNT(*) FROM {AddressModel._model.__table_name__}")[0][0]
    total_pages = int(math.ceil(total_register / limit))

    if page > total_pages:
        page = total_pages
    offset = (page - 1) * limit
    return {"page": page, "pages": total_pages, "limit": limit, "data": AddressModel.limit(limit).offset(offset).select(flavour=dict)}


a = [pagination(x) for x in range(1, 11)]
print("Corrido con exito")
pass
