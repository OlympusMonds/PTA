from decimal import Decimal
from pony.orm import Database, Required, Set, PrimaryKey, sql_debug

# What is up with the scoping of this..
db = Database("sqlite", "database.sqlite", create_db=True)

def init():
    sql_debug(True)
    db.generate_mapping(create_tables=True)


class Origin(db.Entity):
    location = PrimaryKey(str)
    destinations = Set("Destination")


class Destination(db.Entity):
    location = Required(str)
    time = Required(int)
    mode = Required(str)
    duration = Required(int)
    distance = Required(Decimal)
    origin = Required(Origin)
