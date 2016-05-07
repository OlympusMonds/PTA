import geojson
import pony.orm as pny
from flask import Flask
from flask.ext.cache import Cache
from flask_restful import Resource, Api
import logging

from public_transport_analyser.database.database import Origin, init
from public_transport_analyser.visualiser.utils import get_voronoi_map


pta = Flask(__name__)
cache = Cache(pta, config={'CACHE_TYPE': 'simple'})
api = Api(pta)

logger = logging.getLogger('PTA.flask')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


@pta.route("/")
def index():
    logger.info("home page")
    return pta.send_static_file("origins.html")


@pta.route("/faq")
def faq():
    logger.info("faq page")
    return pta.send_static_file("faq.html")


class FetchAllOrigins(Resource):
    @cache.cached(timeout=300)
    def get(self):
        logger.info("Get all origins")

        # Get info from DB
        retrycount = 3
        for _ in range(retrycount):
            try:
                with pny.db_session:
                    origins = pny.select((o.location, pny.count(o.destinations)) for o in Origin)[:]

                break  # DB access went OK, no need to retry

            except ValueError as ve:
                properties = {"num_dest": -1,
                              "isOrigin": True,
                              "location": "error! reload page."}
                f = geojson.Feature(geometry=geojson.Point((151.2, -33.9)), properties=properties)
                return geojson.FeatureCollection([f, ])

            except pny.core.RollbackException as re:
                logger.error("Bad DB hit. Retrying:\n{}".format(re))

        else:
            logger.error("DB failed bigtime.")  # for loop did not break.
            # TODO: deal with this error

        # Prepare GeoJSON
        features = []
        for location, num_dest in origins:
            lat, lon = map(float, location.split(","))
            properties = {"num_dest": num_dest,
                          "isOrigin": True,
                          "location": ",".join(map(str, (lat,lon)))}
            features.append(geojson.Feature(geometry=geojson.Point((lon, lat)), properties=properties))

        return geojson.FeatureCollection(features)


class FetchOrigin(Resource):
    def get(self, origin, time = 6):
        logger.info("Get origins: {}".format(origin))

        # Get info from DB
        retrycount = 3
        for _ in range(retrycount):
            destinations = []

            try:
                with pny.db_session:
                    try:
                        o = Origin[origin]
                    except pny.ObjectNotFound:
                        # TODO: use response codes
                        raise ValueError("No such origin.")

                    num_dest = len(o.destinations)
                    for d in o.destinations:
                        dlat, dlon = map(float, d.location.split(","))

                        driving = -1
                        transit = -1
                        for t in d.trips:
                            if t.mode == "driving":
                                driving = t.duration
                            elif t.time == time:
                                transit = t.duration

                        ratio = -1.0
                        if driving > 0 and transit > 0:
                            ratio = float(driving) / float(transit)

                        destinations.append((dlon, dlat, ratio))
                break
            except pny.core.RollbackException as re:
                logger.error("Bad DB hit. Retrying:\n{}".format(re))
        else:
            logger.error("DB failed bigtime.")
            # TODO: deal with this error

        # Build GeoJSON features
        # Plot the origin point
        features = []
        olat, olon = map(float, origin.split(","))
        properties = {"isOrigin": True,
                      "num_dest": num_dest,
                      "location": (olat, olon),
                      }
        features.append(geojson.Feature(geometry=geojson.Point((olon, olat)), properties=properties))

        # Plot the destination points
        for details in destinations:
            dlon, dlat, ratio = details
            if ratio == -1:
                continue  # Don't send bad data
            properties = {"ratio": ratio,
                          "isDestination": True,
                          "location": (dlon, dlat)}
            features.append(geojson.Feature(geometry=geojson.Point((dlon, dlat)), properties=properties))

        # Plot the destination map
        try:
            regions, vertices = get_voronoi_map(destinations)

            for i, region in enumerate(regions):
                ratio = destinations[i][2]
                if ratio == -1:
                    continue
                properties = {"isPolygon": True,
                              "ratio": ratio}
                points = [(lon, lat) for lon, lat in vertices[region]]  # TODO: do some rounding to save bandwidth
                points.append(points[0])  # close off the polygon

                features.append(geojson.Feature(geometry=geojson.Polygon([points]),
                                                properties=properties, ))
        except ValueError as ve:
            logger.error("Voronoi function failed. Only sending destinations.")

        return geojson.FeatureCollection(features)


api.add_resource(FetchAllOrigins, '/api/origins')
api.add_resource(FetchOrigin, '/api/origin/<string:origin>/<int:time>')

init()  # Start up the DB

if __name__ == "__main__":
    pta.debug = False
    pta.run(host='0.0.0.0')
