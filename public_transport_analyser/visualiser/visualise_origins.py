"""
Mostly for debugging for now, this script uses matplotlib to plot origins,
destinations, and their links. Eventually it will plot the ratio of driving
vs. transit for various times. It is also a prototype for the website that
will no double come later.
"""

import sys
import os
import matplotlib.pyplot as plt

import pony.orm as pny
from public_transport_analyser.database.database import Origin, init
#from public_transport_analyser.data_gatherer.config import bounding_box


def vis():
    #minlat, minlon = bounding_box["minlat"], bounding_box["minlon"]
    #maxlat, maxlon = bounding_box["maxlat"], bounding_box["maxlon"]

    lats, lons = [], []

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]

        for o in origins:
            lat, lon = o.location.split(",")
            lats.append(lat)
            lons.append(lon)

    plt.figure()
    plt.scatter(lons, lats, c="black", s=1)
    plt.axis('equal')
    #plt.xlim(minlon, maxlon)
    #plt.ylim(minlat, maxlat)
    plt.savefig(os.path.join(os.getcwd(), "maps", "origins.png"))
    plt.close()

    print("Number of origins: {}".format(len(lats)))


if __name__ == "__main__":
    init()
    sys.exit(vis())