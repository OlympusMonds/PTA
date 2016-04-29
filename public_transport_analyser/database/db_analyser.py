"""
Mostly for debugging for now, this script uses matplotlib to plot origins,
destinations, and their links. Eventually it will plot the ratio of driving
vs. transit for various times. It is also a prototype for the website that
will no double come later.
"""

import sys
import os

import pony.orm as pny
from public_transport_analyser.database.database import Origin, Destination, Trip, init


def mess():
    with pny.db_session:
        o = Origin["-33.924,151.206"]
        d = Destination.get(location = "-33.907,151.194", origin = o)
        print(o, o.location)
        print(d, d.location)
        print(d in o.destinations)

        print(o.destinations)


def count_origins():
    with pny.db_session:
        origins = pny.select(pny.count(o) for o in Origin).first()
        return origins


def count_destinations():
    with pny.db_session:
        destinations = pny.select(pny.count(d) for d in Destination).first()
        return destinations


def count_trips():
    with pny.db_session:
        trips = pny.select(pny.count(t) for t in Trip).first()
        return trips


def count_origins_with_no_dest():
    num_bad_origins = 0

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]
        for o in origins:
            if len(o.destinations) == 0:
                num_bad_origins += 1
    return num_bad_origins


def route_stats():
    max_trips = -1
    min_trips = 1e6
    avg_trips = 0
    count = 0

    max_route = None

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]
        for o in origins:
            for d in o.destinations:
                num_trips = len(d.trips)
                if num_trips > max_trips:
                    max_trips = num_trips
                    max_route = "{}_{}".format(o.location, d.location)
                max_trips = max(max_trips, num_trips)
                min_trips = min(min_trips, num_trips)
                avg_trips += num_trips
                count += 1

    return max_trips, min_trips, avg_trips/float(count), max_route


def analyser():
    """
    mess()
    """
    print("Number of origins: {}".format(count_origins()))
    print("Number of destinations: {}".format(count_destinations()))
    print("Number of trips: {}".format(count_trips()))


    print("Number of bad origins: {}".format(count_origins_with_no_dest()))

    max_trips, min_trips, avg_trips, max_route = route_stats()
    print("Max trips on a route: {} ({})".format(max_trips, max_route))
    print("Min trips on a route: {}".format(min_trips))
    print("Avg trips on a route: {}".format(avg_trips))



if __name__ == "__main__":
    init()
    sys.exit(analyser())