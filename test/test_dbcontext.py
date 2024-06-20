import os

from orm import MySQLRepository, IRepositoryBase
from orm.condition_types import ConditionType
from test.models.address import AddressModel

from dotenv import load_dotenv

load_dotenv()


USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")


database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()


a_model = AddressModel(database)
address = (
    a_model.where(lambda a: 177 >= a.address_id >= 28)
    .where(lambda x: (x.city.country.country, ConditionType.REGEXP, r"^[FHA]"))
    .where(lambda x: (x.city.city, ConditionType.REGEXP, r"[^W]"))
    .order(lambda a: a.address_id, order_type="DESC")
    .select(
        lambda a: (
            a.address_id,
            a.city.country.country,
            a.city.city,
            a.address,
        ),
        flavour=tuple,
    )
)

query = """
SELECT address.address_id as `kkk`, country.country as `country_country`, city.city as `city_city`, address.address as `address_address` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id
WHERE country.country REGEXP '^[FHA]' AND (city.city REGEXP '[^W]') AND (177 >= address.address_id) AND (address.address_id <= 28)
ORDER BY address.address_id DESC
"""
address = a_model._repository.read_sql(query, flavour=dict)
pass


address = a_model.where(lambda x: x.address_id == 1).select()

address.address2 = "primera vivienda"
a_model.upsert(address)
