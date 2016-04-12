import random
from url_generator import get_urls_for_route


def generate_routes(url_queue):
    minlat, minlon = -33.846351, 151.151910
    maxlat, maxlon = -33.938762, 151.254523

    deltalat = maxlat - minlat
    deltalon = maxlon - minlon

    routes = set()

    while True:
        new_o_lat = minlat + random.random() * deltalat
        new_o_lon = minlon + random.random() * deltalon
        origin = "{},{}".format(new_o_lat, new_o_lon)

        for _ in range(10):
            new_d_lat = minlat + random.random() * deltalat
            new_d_lon = minlon + random.random() * deltalon
            destination = "{},{}".format(new_d_lat, new_d_lon)

            data = get_urls_for_route(origin, destination)

            route = (origin, destination)
            if route in routes:
                continue
            else:
                routes.add(route)
                for url in data["details"]:
                    url_queue.put([data["route"], url])
