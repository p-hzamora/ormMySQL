import dbcontext as db
from datetime import datetime

instance = db.Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())


db.Actor
ad_filter = (
    instance.join(db.City, by="INNER JOIN", where=lambda a, c: a.city_id == c.city_id)
    .join(db.Country, db.City, by="INNER JOIN", where=lambda ci, co: ci.country_id == co.country_id)
    .where(db.Address, lambda a: a.address_id == 2)
    .select(db.Country,lambda c:c.country)
)


print(ad_filter)
