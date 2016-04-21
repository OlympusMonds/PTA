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



def voronoi_finite_polygons_2d(vor, radius=None):
    """
    From: https://gist.github.com/pv/8036995
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.
    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.
    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.
    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def vis():
    minlat, minlon = -33.846351, 151.151910
    maxlat, maxlon = -33.938762, 151.254523

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
                        driving_dur = t.duration
                    else:
                        transit_dur += t.duration
                        count += 1

                avg_transit_dur = transit_dur / count

                ratio = 1 - (driving_dur/avg_transit_dur)
                if ratio > 1:
                    ratio = 1.0


                points.append((dlon, dlat, float(ratio)))

            # compute Voronoi tesselation
            points = np.array(points)

            if points.shape[0] > 4:
                vor = Voronoi(points[:,:2])

                regions, vertices = voronoi_finite_polygons_2d(vor)

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