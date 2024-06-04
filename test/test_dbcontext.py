import dbcontext as db
from datetime import datetime
from orm import Table, Column,ForeignKey

instance = db.Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())


class B(Table):
    __table_name__ = "b"
    pk_b:int = Column(is_primary_key=True)
    name:str
    data:str
    date:datetime
    
class A(Table):
    __table_name__ = "a"
    pk_a:int = Column(is_primary_key=True)
    fk_b:int

    b = ForeignKey["A",B](__table_name__,B,lambda a,b: a.fk_b == b.pk_b)



class C(Table):
    __table_name__ = "c"
    pk_c:int = Column(is_primary_key=True)
    data_c:str
    fk_a:int

    c = ForeignKey["C",A](__table_name__,A,lambda c,a: c.fk_a == a.pk_a)



a = A(1,4)
b = B(4,"pablo","trabajador",datetime.now())

a.b # select b.name for a inner join b on a.fk_b = b.pk_b 
            # output:pablo 

ad_filter = (
    instance.join(db.City, by="INNER JOIN", where=lambda a, c: a.city_id == c.city_id)
    .join(db.Country, db.City, by="INNER JOIN", where=lambda ci, co: ci.country_id == co.country_id)
    .where(db.Address, lambda a: a.address_id == 2)
    .select(db.Country,lambda c:c.country)
)


print(ad_filter)
