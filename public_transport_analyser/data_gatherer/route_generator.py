import random
from url_generator import get_urls_for_route


def generate_routes(bounding_box, map_resolution, url_queue):
    minlat, minlon = bounding_box["minlat"], bounding_box["minlon"]
    maxlat, maxlon = bounding_box["maxlat"], bounding_box["maxlon"]

    deltalat = maxlat - minlat
    deltalon = maxlon - minlon

    while True:
        # Get a random origin within the bounding box, and then round to the
        # map resolution.
        new_o_lat = round(minlat + random.random() * deltalat, map_resolution)
        new_o_lon = round(minlon + random.random() * deltalon, map_resolution)
        origin = "{0},{1}".format(new_o_lat, new_o_lon)

        for _ in range(10):
            # Generate 10 random destinations in the same way from the origin.
            new_d_lat = round(minlat + random.random() * deltalat, map_resolution)
            new_d_lon = round(minlon + random.random() * deltalon, map_resolution)
            destination = "{0},{1}".format(new_d_lat, new_d_lon)

            data = get_urls_for_route(origin, destination)  # make a URL for the route

            for url in data["details"]:
                url_queue.put([data["route"], url])
