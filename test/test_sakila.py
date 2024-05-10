import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

parent = Path(__file__).parent.parent
sys.path.append(str(parent))

from orm import MySQLRepository  # noqa: E402
from models.city import City, CityModel  # noqa: E402
from models.country import Country, CountryModel  # noqa
from models.address import Address, AddressModel  # noqa

load_dotenv()

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

db_sakila = MySQLRepository(
    user=USERNAME,
    password=PASSWORD,
    database="sakila",
    host="localhost",
).connect()


city_model: CityModel = CityModel(db_sakila)
country_model: CountryModel = CountryModel(db_sakila) 
address_model: AddressModel = AddressModel(db_sakila) 


# city = model_city.all()
# country = model_country.all(flavour=tuple)
c = City(None,"custom_city",87,datetime.now())
city = city_model.filter_by(lambda x: x.country_id < 20).get(lambda x: x.country.last_update)
pass