import pony.orm as pny
from public_transport_analyser.database.database import Origin, Destination, Trip
from public_transport_analyser.data_gatherer.PTEexceptions import ZeroResultsError


def process_data(bad_routes, data_queue):
    while True:
        route_info, reqjson = data_queue.get()

        try:
            duration, distance = process_response(reqjson)
            save_to_db(route_info, duration, distance)

        except ZeroResultsError:
            """
            ZeroResultsError typically means the route generator put the origin or the destination
            in a body of water or something.
            """
            print("No results for that route; result skipped.")
            bad_routes.add(route_info["route"])
            if len(bad_routes) > 100e3:
                bad_routes.clear()  # Make sure things don't get out of hand.

        except ValueError:
            print("Returned data doesn't match expected data structure; result skipped.")

        finally:
            data_queue.task_done()


def process_response(reqjson):
    """
    Extract/process the data returned in the request to return the needed information.
    :param data: the JSON data of the request
    :return: list(duration, distance) of the particular trip.
    """
    try:
        if data["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
            raise ZeroResultsError("No results found")

        duration = data["rows"][0]["elements"][0]["duration"]["value"]
        distance = data["rows"][0]["elements"][0]["distance"]["value"]

    except (KeyError, IndexError) as e:
        raise ValueError("Exception: {0}".format(e))

    return duration, distance


def save_to_db(route_info, duration, distance):
    """
    Save the route info to the DB. Search for existing DB entries first, and
    add to them if needed, otherwise generate new entries.
    :param route: string of the origin and destination, joined with a "_"
    :param duration: time in seconds of the trip
    :param distance: distance in meters of the trip
    :return: none
    """
    origin, dest = route_info["route"].split("_")
    print("  DB: saving {}.".format(route_info["route"]))
    with pny.db_session:
        """
        Fetch the origin and dest from the DB, or create if they don't
        exist. Once obtained, make a new trip between them storing the
        results.
        """
        if Origin.exists(location = origin):
            o = Origin.get(location = origin)
        else:
            o = Origin(location = origin)

        if Destination.exists(location = dest):
            d = Destination.get(location = dest)
        else:
            d = Destination(location = dest, origin = o)

        t = Trip(mode = route_info["mode"],
                 time = route_info["hour"],
                 duration = duration,
                 distance = distance,
                 destination = d)
        d.trips.add(t)
