"""
Mostly for debugging for now, this script uses matplotlib to plot origins,
destinations, and their links. Eventually it will plot the ratio of driving
vs. transit for various times. It is also a prototype for the website that
will no double come later.
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from scipy.spatial import Voronoi
import numpy as np

import pony.orm as pny
from public_transport_analyser.database.database import Origin, init
from public_transport_analyser.rest_backend.utils import voronoi_finite_polygons_2d
from public_transport_analyser.data_gatherer.config import bounding_box


def vis():
    minlat, minlon = bounding_box["minlat"], bounding_box["minlon"]
    maxlat, maxlon = bounding_box["maxlat"], bounding_box["maxlon"]

    jet = plt.get_cmap('jet')
    cNorm = colors.Normalize(vmin=0, vmax=1)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]

        for o in origins:
            plt.figure()

            lat, lon = o.location.split(",")
            plt.scatter(lon, lat, c="black", s=100)

            points = []

            for d in o.destinations:
                dlat, dlon = d.location.split(",")

                count = 0
                driving_dur = 0
                transit_dur = 0
                for t in d.trips:
                    if t.mode == "driving":
                        driving_dur = float(t.duration)
                    else:
                        transit_dur += float(t.duration)
                        count += 1

                try:
                    avg_transit_dur = transit_dur / count
                    ratio = 1 - (driving_dur / avg_transit_dur)
                except ZeroDivisionError:
                    print("Division by 0 error for:\n origin: {0}\n destin: {1}".format(o, d))
                except Exception as e:
                    print("Unknown exception:\n{0}\n".format(e))

                if ratio > 1:
                    ratio = 1.0

                points.append((dlon, dlat, float(ratio)))

            # compute Voronoi tesselation
            points = np.array(points)

            if points.shape[0] > 4:
                vor = Voronoi(points[:,:2])

                regions, vertices = voronoi_finite_polygons_2d(vor, 0.08)

                # colorize
                for i, region in enumerate(regions):
                    polygon = vertices[region]
                    plt.fill(*zip(*polygon), alpha=0.3)

                plt.scatter(points[:, 0], points[:, 1], s=20, c=points[:, 2])
                plt.axis('equal')
                plt.xlim(minlon, maxlon)
                plt.ylim(minlat, maxlat)

                filename = "origin_{0}_{1}.png".format(lat, lon)
                print("Saving {0}".format(filename))
                plt.savefig(os.path.join(os.getcwd(), "maps", filename))
            plt.close()


if __name__ == "__main__":
    init()
    sys.exit(vis())