from decimal import Decimal
from pony.orm import Database, Required, Set, PrimaryKey, sql_debug

# What is up with the scoping of this..
db = Database("sqlite", "database.sqlite", create_db=False)


def init():
    sql_debug(False)
    db.generate_mapping(check_tables=True, create_tables=False)


def create():
    db.generate_mapping(create_tables=True)


class Origin(db.Entity):
    location = PrimaryKey(str)
    destinations = Set("Destination")


class Destination(db.Entity):
    """
    This class maps back only one origin - yet, you could feasibly have
    more than one origin pointing to the same destination (implying a
    many to many relationship). However, at the moment, I can't see a
    reason why it would be better do than the current setup, and one
    imagines you would only care about where you start, rather than all
    the potential starts at the end.
    """
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