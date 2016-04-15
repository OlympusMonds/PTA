from decimal import Decimal
from pony.orm import Database, Required, Set, PrimaryKey, sql_debug

# What is up with the scoping of this..
db = Database("sqlite", "database.sqlite", create_db=True)

def init():
    sql_debug(False)
    db.generate_mapping(create_tables=True)


class Origin(db.Entity):
    location = PrimaryKey(str)
    destinations = Set("Destination")


class Destination(db.Entity):
    id = PrimaryKey(int, auto=True)
    location = Required(str)
    origin = Required(Origin)
    trips = Set("Trip")


class Trip(db.Entity):
    id = PrimaryKey(int, auto=True)
    time = Required(int)
    mode = Required(str)
    distance = Required(int)
    duration = Required(Decimal)
    destination = Required(Destination)