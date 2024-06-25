import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import math

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from orm import MySQLRepository, IRepositoryBase  # noqa: E402
from orm.condition_types import ConditionType  # noqa: E402
from test.models.address import AddressModel, Address  # noqa: E402


load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()


a_model = AddressModel(database)
res_tuple_3 = (
    a_model.where(lambda a: a.address_id <= 5)
    .order(lambda a: a.address_id, order_type="DESC")
    .select(
        lambda a: (
            a,
            a.city,
            a.city.country.country_id,
        )
    )
)

res_one_table_five_results = a_model.where(lambda a: a.address_id <= 5).order(lambda a: a.address_id, order_type="DESC").select(lambda a: (a.city,))
res_one_table_five_results = a_model.where(lambda a: a.address_id ==5).order(lambda a: a.address_id, order_type="DESC").select()


query = """
SELECT address.address_id as `kkk`, country.country as `country_country`, city.city as `city_city`, address.address as `address_address` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id
WHERE country.country REGEXP '^[FHA]' AND (city.city REGEXP '[^W]') AND (177 >= address.address_id) AND (address.address_id <= 28)
ORDER BY address.address_id DESC
"""
address = a_model._repository.read_sql(query, flavour=dict)
pass


def pagination(page: int):
    limit = 20
    total_register: int = a_model._repository.read_sql(f"SELECT COUNT(*) FROM {a_model._model.__table_name__}")
    total_pages = int(math.ceil(total_register / limit))

    if page > total_pages:
        page = total_pages
    offset = (page - 1) * limit
    return {"page": page, "pages": total_pages, "limit": limit, "data": a_model.limit(limit).offset(offset).select(flavour=dict)}


a = [pagination(x) for x in range(1, 11)]

pass
