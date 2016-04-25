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
    data = make_json()
    return str(data)  # TODO: this makes array() and ' instead of "


def make_json():

    regions, vertices = get_data()

    features = []

    for r in regions:
        points = [(lat, lon) for lat, lon in vertices[r]]
        points.append(points[0])
        p = geojson.Polygon([points])
        feature = geojson.Feature(geometry=p)
        features.append(feature)

    fc = geojson.FeatureCollection(features)
    return geojson.dumps(fc, sort_keys=True)


def get_data():

    with pny.db_session:
        origins = pny.select(o for o in Origin)[:]

        for o in origins:
            points = []
            lat, lon = o.location.split(",")

            for d in o.destinations:
                dlat, dlon = d.location.split(",")

                points.append((dlon, dlat))
            points = np.array(points)

            if points.shape[0] > 4:
                vor = Voronoi(points)
                return voronoi_finite_polygons_2d(vor, 0.05)


if __name__ == "__main__":
    init()
    ask_flask.debug = True
    ask_flask.run()
