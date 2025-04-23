import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.env import DATABASE_URL

from ormlambda import ORM, create_engine, Table, Column

db = create_engine(DATABASE_URL)

class Address(Table):
    __table_name__ = "address"

    address_id: Column[int] = Column(int, is_primary_key=True)
    address: Column[str]
    address2: Column[str]
    district: Column[str]
    city_id: Column[int]
    postal_code: Column[str]
    phone: Column[str]
    location: Column[None | bytes]

db.execute_with_values(
    """
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name=?;
    """,('movie'))
if not db.database_exists("movie"):
    db.execute("CREATE TABLE movie(title, year, score)")
db.execute("""
INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)            
""")

result = db.read_sql("SELECT score,title FROM movie",flavour=dict)
ORM(Address, db).create_table()
