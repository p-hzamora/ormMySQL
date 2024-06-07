from datetime import datetime

import dbcontext as db

from orm import MySQLRepository, IRepositoryBase

from test.models import AddressModel

from dotenv import load_dotenv

load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


# db_common = MySQLRepository(user=USERNAME, password=PASSWORD, database="common", host=HOST).connect()

database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()

address = db.Address(address_id=10)

a_model = AddressModel(database)


filtro = a_model.where(address, lambda a: a.address_id == 10).select(
    lambda a: (
        a,
        a.city,
        a.city.country,
    )
)
# a = a_model.select(lambda a: (a.address, a.city_id))

pass
