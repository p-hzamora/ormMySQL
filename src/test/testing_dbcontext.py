import sys
from pathlib import Path
from decouple import config
import math

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql import MySQLRepository  # noqa: E402
from ormlambda import IRepositoryBase  # noqa: E402
from ormlambda.databases.my_sql.clauses.joins import JoinType  # noqa: E402
from models.staff import StaffModel, Staff  # noqa: E402
from models.address import AddressModel, Address  # noqa: E402
from models.actor import ActorModel, Actor  # noqa: E402
from models.store import StoreModel  # noqa: E402


USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
HOST = config("HOST")

a = Staff.find_dependent_tables()

database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST)

actor_model = ActorModel(database)
store_model = StoreModel(database)
a_model = AddressModel(database)
s_model = StaffModel(database)


result = (
    AddressModel(database)
    .where(Address.City.Country.country_id == 87)
    .select(
        lambda address: (
            address.city_id,
            address.City.city_id,
            address.City.country_id,
            address.City.Country.country_id,
        ),
        flavour=tuple,
    )
)
res = a_model.where(Address.City.Country.country.regex(r"^[aA]")).select(
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
s_model.repository.create_database(asdf, "replace")
s_model.repository.drop_database(asdf)


staff = s_model.where(Staff.staff_id == 1).select_one()
staff.staff_id = 100
s_model.upsert(staff)
id = s_model.order(lambda x: x.staff_id, order_type="DESC").select_one().staff_id
new_staff = s_model.where(Staff.staff_id == id).select_one()
new_staff.first_name = "PEPON"
s_model.upsert(new_staff)

staffs = s_model.where(Staff.staff_id > 2).delete()


res_tuple_3 = (
    a_model.order(lambda a: a.address_id, order_type="DESC")
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
    a_model.order(lambda a: a.address_id, order_type="DESC")
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


res_one_table_five_results = a_model.where(Address.address_id <= 5).limit(100).order(lambda a: a.address_id, order_type="DESC").select(lambda a: (a,))
res_one_table_one_result = a_model.where(Address.address_id == 5).order(lambda a: a.address_id, order_type="DESC").select_one()
res_one_table_one_result = a_model.where(Address.address2 == 100).order(lambda a: a.address_id, order_type="DESC").select_one(lambda x: x)


query = """
SELECT address.address_id as `kkk`, country.country as `country_country`, city.city as `city_city`, address.address as `address_address` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id
WHERE country.country REGEXP '^[FHA]' AND (city.city REGEXP '[^W]') AND (177 >= address.address_id) AND (address.address_id <= 28)
ORDER BY address.address_id DESC
"""
address = a_model.repository.read_sql(query, flavour=dict)
pass


def pagination(page: int):
    limit = 20
    total_register: int = a_model.repository.read_sql(f"SELECT COUNT(*) FROM {a_model._model.__table_name__}")[0][0]
    total_pages = int(math.ceil(total_register / limit))

    if page > total_pages:
        page = total_pages
    offset = (page - 1) * limit
    return {"page": page, "pages": total_pages, "limit": limit, "data": a_model.limit(limit).offset(offset).select(flavour=dict)}


a = [pagination(x) for x in range(1, 11)]
print("Corrido con exito")
pass
