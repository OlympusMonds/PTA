"""
Mostly for debugging for now, this script uses matplotlib to plot origins,
destinations, and their links. Eventually it will plot the ratio of driving
vs. transit for various times. It is also a prototype for the website that
will no double come later.
"""

import sys
import pony.orm as pny
from database import Origin, Destination
from database import init

import matplotlib.pyplot as plt


def vis():
    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]

        for o in origins:
            lat, lon = o.location.split(",")
            plt.scatter(lon, lat, c="r", s=100)

            for d in o.destinations:
                dlat, dlon = d.location.split(",")
                plt.scatter(dlon, dlat)
                plt.plot([lon, dlon], [lat, dlat], c="black")

            plt.show()





if __name__ == "__main__":
    init()
    sys.exit(vis())