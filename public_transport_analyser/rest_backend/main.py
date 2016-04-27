import pony.orm as pny
from flask import Flask, url_for, redirect
import numpy as np
from scipy.spatial import Voronoi
import geojson

from public_transport_analyser.database.database import Origin, init
from public_transport_analyser.rest_backend.utils import voronoi_finite_polygons_2d

ask_flask = Flask(__name__)


@ask_flask.route("/")
def index():
    return "Put an origin in the url"


@ask_flask.route("/<origin>")
def get_routes_from_origin(origin):
    try:
        rest_json = make_json(origin)
    except ValueError as ve:
        return str(ve)

    return rest_json


@ask_flask.route("/origins")
def get_origins():
    lonlats = []

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]

        for o in origins:
            lat, lon = o.location.split(",")
            lonlats.append((float(lon), float(lat)))

    features = []
    for origin in lonlats:
        properties = {"location": "g"}#""{}".format(origin),}
        features.append(geojson.Feature(geometry=geojson.Point(origin), properties=properties))

    fc = geojson.FeatureCollection(features)
    return geojson.dumps(fc, sort_keys=True)


def make_json(origin):

    regions, vertices = get_data(origin)

    features = []
    properties = {"color": "blue",
                  "strokeWeight": "1",}

    for r in regions:
        points = [(lon, lat) for lat, lon in vertices[r]]
        points.append(points[0])  # close off the polygon

        features.append(geojson.Feature(geometry=geojson.Polygon([points]),
                                        properties=properties,))

    fc = geojson.FeatureCollection(features)
    return geojson.dumps(fc, sort_keys=True)


def get_data(origin):

    with pny.db_session:
        if Origin.exists(location=origin):
            o = Origin.get(location=origin)
        else:
            raise ValueError("No such origin.")

        points = []
        lat, lon = o.location.split(",")

        for d in o.destinations:
            dlat, dlon = d.location.split(",")

            points.append((dlon, dlat))
        points = np.array(points)

        if points.shape[0] > 4:
            vor = Voronoi(points)
        else:
            raise ValueError("Not enough points to construct map. "
                             "Points = {}, need >4.".format(points.shape))

        return voronoi_finite_polygons_2d(vor, 0.05)


if __name__ == "__main__":
    init()
    ask_flask.debug = True
    ask_flask.run()
