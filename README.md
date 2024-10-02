![PyPI version](https://img.shields.io/pypi/v/ormlambda.svg)
![downloads](https://img.shields.io/pypi/dm/ormlambda?label=downloads)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

# ormMySQL
This ORM is designed to connect with a MySQL server, facilitating the management of various database queries. Built with flexibility and efficiency in mind, this ORM empowers developers to interact with the database using lambda functions, allowing for concise and expressive query construction. 

# Creating your first lambda query

## Initialize MySQLRepository
```python
from decouple import config
from ormlambda.databases.my_sql import MySQLRepository

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
HOST = config("HOST")


database = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST)
```

## Select all columns
```python
from models.address import AddressModel

result = AddressModel(database).select()
```
The `result` var will be of type `tuple[Address, ...]` 

## Select multiples tables
Once the `AddressModel` class is created, we will not only be able to access all the information in that table, but also all the information in all the tables that have foreign keys related to it."

```python
from ormlambda import ConditionType
from models.address import AddressModel


result = AddressModel(database).where(lambda x: (x.City.Country, ConditionType.REGEXP, r"^[aA]")).select(
    lambda address: (
        address,
        address.City,
        address.City.Country,
    ),
)
```
The `result` var will be of type `tuple[tuple[Address], tuple[City], tuple[Country]]`.

If we were used `select_one` method, we retrieved `tuple[Address, City, Country]`.

## Filter by `where` condition

```python
result = AddressModel(database).where(lambda x: 10 <= x.address_id <= 30).select()
```

Additionally, we can filter by others tables. For example, we can return all addresses for each city where `country_id` = 87 (Spain)

```python
result = AddressModel(database).where(lambda x: x.City.Country.country_id  == 87).select()
```

We can also return `Address`, `City` or `Country` if needed.

```python
result = AddressModel(database).where(lambda x: x.City.Country.country_id == 87).select(lambda x: (x, x.City, x.City.Country))
```

### Pass variables to the `where` method
Since we generally work with lambda methods, I often have to work with `bytecode` to retrieve the name of the string variables. For this reason, it's imperative that we map these variables to replace them with the actual values.

```python
LOWER = 10
UPPER = 30
AddressModel(database).where(lambda x: LOWER <= x.address_id <= UPPER, LOWER=LOWER, UPPER=UPPER).select()
```
That solution is somewhat `awkward` and not very clean, but it's necessary for automating queries.

## Writable methods INSERT, UPDATE, DELETE
The easiest way to add or delete data in your database is by using its appropiate methods. You just need to instantiate an object with the data and pass it to the method

### Insert
```python
address = Address(address_id=1, address="C/ ...", phone="XXXXXXXXX", postal_code="28026")

AddressModel(database).insert(address)
```

### Update

You can use either the properties of the same object or `str` values.
```python

AddressModel(database).where(lambda x: x.address_id == 1).update(
    {
        Address.phone: "YYYYYYYYY",
        Address.postal_code: "28030",
    }
)

AddressModel(database).where(lambda x: x.address_id == 1).update(
    {
        "phone": "YYYYYYYYY",
        "postal_code": "28030",
    }
)
```
### Delete

```python
AddressModel(database).where(lambda x: x.address_id == 1).delete()
```


# Table Map
The most important aspect when creating classes to map database tables is to consider the importance of typing the variables that should behave as columns. In other words, variables that are typed will be those that are passed to the class constructor. This is why both `__table_name__` and variables that reference foreign classes, are not given a specific data tpye.

For example, imagine you have three Table in your database: `Addres`, `City` and `Country`. Each of them has its own Foreing keys.

`Address` has a FK relationship with `City`.

`City` has a FK relationship with `Country`.

The easiest way to map your tables is:

```python
from datetime import datetime

from ormlambda import (
    Column,
    Table,
    BaseModel,
    ForeignKey,
)
from ormlambda.common.interfaces import IStatements_two_generic, IRepositoryBase


class Country(Table):
    __table_name__ = "country"

    country_id: int = Column[int](is_primary_key=True)
    country: str
    last_update: datetime


class Address(Table):
    __table_name__ = "address"

    address_id: int = Column[int](is_primary_key=True)
    address: str
    address2: str
    district: str
    city_id: int
    postal_code: str
    phone: str
    location: str
    last_update: datetime = Column[datetime](is_auto_generated=True)

    City = ForeignKey["Address", City](__table_name__, City, lambda a, c: a.city_id == c.city_id)


class City(Table):
    __table_name__ = "city"

    city_id: int = Column[int](is_primary_key=True)
    city: str
    country_id: int
    last_update: datetime

    Country = ForeignKey["City", Country](__table_name__, Country, lambda ci, co: ci.country_id == co.country_id)
```

Once created, you need to create a Model for each Table

```python
class CountryModel(BaseModel[Country]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Country, repository)


class AddressModel(BaseModel[Address]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, Address, repository)


class CityModel(BaseModel[City]):
    def __new__[TRepo](cls, repository: IRepositoryBase[TRepo]):
        return super().__new__(cls, City, repository)
```

# Creating complex queries with lambda

We can use various methods such as `where`, `limit`, `offset`, `order`, etc... 

# Filter using `where` method
To retrieve all `Address` object where the fk reference to the `City` table, and the fk reference to the `Country` table have a `country_id` value greater or equal than 50, ordered in `descending` order, then:

```python
result = (
    AddressModel(database)
    .order(lambda a: a.address_id, order_type="DESC")
    .where(lambda x: x.City.Country.country_id >= 50)
    .select(lambda a: (a))
)

```
Also you can use `ConditionType` enum for `regular expressions` and get, for example, all rows from a different table where the `Country` name starts with `A`, limited to `100`:


```python
address, city, country = (
    AddressModel(database)
    .order(lambda a: a.address_id, order_type="DESC")
    .where(lambda x: (x.City.Country, ConditionType.REGEXP, r"^[A]"))
    .limit(100)
    .select(
        lambda a: (
            a,
            a.City,
            a.City.Country,
        )
    )
)


for a in address:

    print(a.address_id)

for c in city:
    print(c.city_id)

for co in country:
    print(co.country)
```

# Transform Table objects into Iterable object
In the example above, we see that the `result` var returns a tuple of tuples. However, we can simplify the `result` var when needed by passing `flavour` attribute in `select` method to get a tuple of the specified data type.

```python
result = (
    a_model
    .where(lambda x: (x.City.Country, ConditionType.REGEXP, r"^[A]"))
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
```

with this approach, we will obtain a dictionary where the key will be the concatenation between the selected table name and the column name specified in the lambda function, to avoid overwritting data from tables that sharing column names.

