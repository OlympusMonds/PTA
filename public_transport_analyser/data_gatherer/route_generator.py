import random
import logging
import pony.orm as pny
from public_transport_analyser.data_gatherer.url_generator import get_info_for_route
from public_transport_analyser.database.database import Origin


def generate_routes(name, bounding_box, map_resolution, reuse_origins, url_queue):
    logger = logging.getLogger('PTA.gen_routes  ')
    minlat, minlon = bounding_box["minlat"], bounding_box["minlon"]
    maxlat, maxlon = bounding_box["maxlat"], bounding_box["maxlon"]

    deltalat = maxlat - minlat
    deltalon = maxlon - minlon

    while True:
        if reuse_origins:
            # Get a random existing origin
            # TODO: this doesn't obey the bounding box
            for _ in range(retries):
                try:
                    logger.debug("Trying to access the DB for an origin")
                    with pny.db_session:
                        origin = Origin.select_random(limit=1)[0]
                        o_lat, o_lon = origin.location.split(",")
                    
                    break
                    logger.debug("DB access went OK.")

                except pny.core.RollbackException:
                    logger.error("DB access failed. Retrying...")
            else:
                logger.error("DB access really failed")
                #TODO: deal with this error.

        else:
            # Get a random origin within the bounding box, and then round to the
            # map resolution.
            o_lat = round(minlat + (random.random() * deltalat), map_resolution)
            o_lon = round(minlon + (random.random() * deltalon), map_resolution)

        origin = "{0},{1}".format(o_lat, o_lon)
        logger.info("{name} picked origin: {origin}".format(name=name, origin=origin))

        for _ in range(10):
            # Generate 10 random destinations in the same way from the origin.
            new_d_lat = round(minlat + (random.random() * deltalat), map_resolution)
            new_d_lon = round(minlon + (random.random() * deltalon), map_resolution)
            destination = "{0},{1}".format(new_d_lat, new_d_lon)
            route = "{0}_{1}".format(origin, destination)
            logger.info("{name} formed route: {route}".format(name=name, route=route))

            for ri in get_info_for_route(route):  # make a URL for the route:
                url_queue.put(ri)
                logger.debug("{name} inserted route {route} into queue with: {ri}".format(name=name, route=route, ri=ri))
