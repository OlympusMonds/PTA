import random
from url_generator import get_urls_for_route


def generate_routes(url_queue):
    minlat, minlon = -33.846351, 151.151910
    maxlat, maxlon = -33.938762, 151.254523

    deltalat = maxlat - minlat
    deltalon = maxlon - minlon

    routes = set()
    route_resolution = 4

    while True:
        if len(routes) > 10e6:  # Ensure routes doesn't get too big..
            routes = set()

        new_o_lat = round(minlat + random.random() * deltalat, route_resolution)
        new_o_lon = round(minlon + random.random() * deltalon, route_resolution)
        origin = "{},{}".format(new_o_lat, new_o_lon)

        for _ in range(10):
            new_d_lat = round(minlat + random.random() * deltalat, route_resolution)
            new_d_lon = round(minlon + random.random() * deltalon, route_resolution)
            destination = "{},{}".format(new_d_lat, new_d_lon)

            data = get_urls_for_route(origin, destination)

            route = (origin, destination)
            if route in routes:
                continue
            else:
                routes.add(route)
                for url in data["details"]:
                    url_queue.put([data["route"], url])
