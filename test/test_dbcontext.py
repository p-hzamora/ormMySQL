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

address = db.Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())

a_model = AddressModel(database)

# filtro = a_model.where(address, lambda a: a.address_id == 1).select(lambda a:( a, a.city, a.city.country))
filtro2 = a_model.select(lambda a: (a, a.city.country.country_id))

address,country = filtro2

pass
