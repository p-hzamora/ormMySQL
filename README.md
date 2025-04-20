![PyPI version](https://img.shields.io/pypi/v/ormlambda.svg)
![downloads](https://img.shields.io/pypi/dm/ormlambda?label=downloads)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

# ormlambda Documentation
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
from ormlambda import ORM
from ormlambda import create_engine

from models.address import Address
from test.config import config_dict

db = create_engine('mysql://root:1234@localhost:3306/sakila')

AddressModel = ORM(Address, db)

result = AddressModel.select()
```
The `result` var will be of type `tuple[Address, ...]` 

## Improving Typing
For those cases where you need to pass the database configuration from a `dict`, you can use `MySQLArgs` TypedDict object to improve type annotations.

```python
from ormlambda.databases.my_sql.types import MySQLArgs

config_dict: MySQLArgs = {
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_DATABASE,
}
db = MySQLRepository(**config_dict)
```

## Select multiples tables
Once the `AddressModel` class is created, we will not only be able to access all the information in that table, but also all the information in all the tables that have foreign keys related to it."

```python
from models.address import Address
from ormlambda import create_engine, ORM

db = create_engine('mysql://root:1234@localhost:3306/sakila')


AddressModel = ORM(Address, db)

result = AddressModel.where(Address.City.Country.country.regex(r"^[aA]")).select(
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

we can use only the Original Table to pass the variables like
```python
result = AddressModel.where(
    [
        Address.address_id >= 10,
        Address.address_id <= 30,
    ]
).select()
```
Or by using a lambda function that returns an iterable for tables where the name is unusually long.

```python
result = AddressModel.where(
    lambda x: [
        x.address_id >= 10,
        x.address_id <= 30,
    ]
).select()

```
Additionally, we can filter by others tables. For example, we can return all addresses for each city where `country_id` = 87 (Spain)

```python
result = AddressModel.where(Address.City.Country.country_id  == 87).select()
```

We can also return `Address`, `City` or `Country` if needed.

```python
result = AddressModel.where(Address.City.Country.country_id == 87).select(lambda x: (x, x.City, x.City.Country))
```

### Pass variables to the `where` method
```python
LOWER = 10
UPPER = 30

AddressModel.where(
    [
        Address.address_id >= LOWER,
        Address.address_id <= UPPER,
    ]
).select()
```


## Writable methods INSERT, UPDATE, DELETE
The easiest way to add or delete data in your database is by using its appropiate methods. You just need to instantiate an object with the data and pass it to the method

### Insert
```python
address = Address(address_id=1, address="C/ ...", phone="XXXXXXXXX", postal_code="28026")

AddressModel.insert(address)
```

### Update
You can use either the properties of the same object or `str` values.
```python

AddressModel.where(lambda x: x.address_id == 1).update(
    {
        Address.phone: "YYYYYYYYY",
        Address.postal_code: "28030",
    }
)

AddressModel.where(lambda x: x.address_id == 1).update(
    {
        "phone": "YYYYYYYYY",
        "postal_code": "28030",
    }
)
```
### Delete

```python
AddressModel.where(lambda x: x.address_id == 1).delete()
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
    Table,
    Column,
    ForeignKey,
)

class Country(Table):
    __table_name__ = "country"

    country_id: Column[int] = Column(int, is_primary_key=True)
    country: Column[str]
    last_update: Column[datetime]


class City(Table):
    __table_name__ = "city"

    city_id: Column[int] = Column(int, is_primary_key=True)
    city: Column[str]
    country_id: Column[int]
    last_update: Column[datetime]

    Country = ForeignKey["City", Country](Country, lambda ci, co: ci.country_id == co.country_id)


class Address(Table):
    __table_name__ = "address"

    address_id: Column[int] = Column(int, is_primary_key=True)
    address: Column[str]
    address2: Column[str]
    district: Column[str]
    city_id: Column[int]
    postal_code: Column[str]
    phone: Column[str]
    location: Column[str]
    last_update: Column[datetime] = Column(datetime, is_auto_generated=True)

    City = ForeignKey["Address", City](City, lambda a, c: a.city_id == c.city_id)

```

# Creating complex queries with lambda

We can use various methods such as `where`, `limit`, `offset`, `order`, etc... 

# Filter using `where` method
To retrieve all `Address` object where the fk reference to the `City` table, and the fk reference to the `Country` table have a `country_id` value greater or equal than 50, ordered in `descending` order, then:

```python
result = (
    AddressModel
    .order(lambda a: a.address_id, order_type="DESC")
    .where(lambda x: x.City.Country.country_id >= 50)
    .select(Address)
)

```
Also you can use `ConditionType` enum for `regular expressions` and get, for example, all rows from a different table where the `Country` name starts with `A`, limited to `100`:


```python
address, city, country = (
    AddressModel
    .order(Address.address_id, order_type="DESC")
    .where(Address.City.Country.country.regex(r"^[A]"))
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
    AddressModel.where(Address.City.Country.country.regex(r"^[A]"))
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

# Other methods

## max
```python
res = AddressModel.max(Address.address_id, execute=True)
```
## min
```python
res = AddressModel.min(Address.address_id, execute=True)
```
## sum
```python
res = AddressModel.sum(Address.address_id, execute=True)
```
## count
```python
res = AddressModel.count(Address.address_id, execute=True)
```

## 1. Concat

The `concat` method allows you to concatenate multiple columns or values into a single string. This is particularly useful for creating derived fields in your queries.

### Usage

```python
response = ORM(Address, db).where(Address.City.Country.country.regex(r"^Spain")).first(
            (
                Address.address,
                Address.City.city,
                self.tmodel.concat(
                    (
                        "Address: ",
                        Address.address,
                        " - city: ",
                        Address.City.city,
                        " - country: ",
                        Address.City.Country.country,
                    )
                ),
            ),
            flavour=dict,
        )

{
    "address_address": "939 Probolinggo Loop",
    "city_city": "A Coruña (La Coruña)",
    "CONCAT": "Address: 939 Probolinggo Loop - city: A Coruña (La Coruña) - country: Spain",
}
```
As you can see in the response, the result is a dictionary where the keys are a combination of the table name and the column name. This is done to avoid collisions with columns from other tables that might have the same name.

Another elegant approach to adjust the response and obtain an object is by using the `flavour` attribute. You can pass a callable object, which will be used to instantiate it with the returned data.


## 2. Group by

The `groupby` method is used to filter results based on aggregate functions.

### Usage
```python
from ormlambda import Column, ORM, create_engine
from test.config import DATABASE_URL


class Response(BaseModel):
    district: str
    count: int

engine= create_engine(DATABASE_URL)
model = ORM(Address,engine)

count_name = Column(column_name="count")

res = (
    self.model
    .groupby(Address.district)
    .select(
        (
            Address.district,
            self.model.count(Address.address),
        ),
        flavour=Response,
    )
)
```

## 3. Having

The `having` method is used to filter results based on aggregate functions. It is typically used in conjunction with `group by` clauses.

### Usage
```python
res = (
    model
    .groupby(Address.district)
    .having(count_name > 4)
    .select(
        (
            Address.district,
            model.count(Address.address),
        ),
        flavour=Response,
    )
)
```


## Using BaseModel for Custom Responses (Pydantic)

You can utilize `BaseModel` from Pydantic to create structured response models. This allows you to define the expected structure of your data, ensuring type safety and validation.

### Example: Creating a Custom Response Model

You can create a custom response model by subclassing `BaseModel`. In this model, you define the fields that you expect in your response, along with their types.

```python
class AddressCombine(BaseModel):
    address: str
    city: str
    country: str

    model_config: ConfigDict = {"extra": "forbid"}

db = create_engine('mysql://root:1234@localhost:3306/sakila')

select = (
    ORM(Address, db)
    .order(lambda x: x.City.Country.country, "DESC")
    .limit(10)
    .where(Address.City.Country.country == "Spain")
    .first(
        lambda x: (
            x.address,
            x.City.city,
            x.City.Country.country,
        ),
        flavour=AddressCombine,
    )
)
```

Once you execute the query, the result will be an instance of your custom model. You can access the fields directly, ensuring that the data adheres to the structure you defined.

```python


print(select.address)
print(select.city)
print(select.country)
```

## Combine aggregation method
As shown in the previous examples, setting the `execute` attribute to `True` allows us to perform the corresponding query in a single line. However, if you're looking to improve efficiency, you can combine all of them into one query.
```python
result = AddressModel.select_one(
            lambda x: (
                AddressModel.min(x.address_id),
                AddressModel.max(x.address_id),
                AddressModel.count(x.address_id),
            ),flavour=dict
        )
```
Getting something like

```python
# {
#     "min": 1,
#     "max": 605,
#     "count": 603,
# }
```

You also can use custom alias for each method

```python
AddressModel.select_one(
    lambda x: (
        AddressModel.min(x.address_id),
        AddressModel.max(x.address_id, alias="custom-max"),
        AddressModel.count(x.address_id),
    ),
    flavour=dict,
)

# {
#     "min": 1,
#     "custom-max": 605,
#     "count": 603,
# }
```