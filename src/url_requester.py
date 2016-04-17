import requests
import time
import pony.orm as pny
from database import Origin, Destination, Trip
from PTEexceptions import ZeroResultsError


def request_urls(url_queue):
    """
    Request the route from Google at a steady pace that does not exceed the usage
    limits. If the data is OK, save it to the database.
    :param url_queue: The queue of URLs to process
    :return: None, the while loop should run forever.
    """

    total_requests_today = 0
    day_in_sec = 3600*24
    max_daily_requests = 2500
    request_rate = day_in_sec / max_daily_requests

    bad_routes = set()

    while True:
        route, details = url_queue.get()
        print(total_requests_today, details["url"])

        try:
            r = requests.get(details["url"])

            if r.status_code == 200:
                duration, distance = process_response(r.json())
                save_to_db(route, details, duration, distance)
            else:
                print("Bad response from Google.")

        except ZeroResultsError:
            print("An error has occurred; result is skipped.")
            bad_routes.add(route)
            if len(bad_routes) > 100e3:
                bad_routes.clear()  # Make sure things don't get out of hand.
        except ValueError:
            print("Returned data doesn't match expected data structure;"
                  " result is skipped.")
        finally:
            """
            No matter what happens, we still need to know how many requests have been
            done, we still need to not spam Google with requests, and we need to tell
            the queue we're done.
            """
            total_requests_today += 1
            url_queue.task_done()
            time.sleep(request_rate)

        if total_requests_today >= max_daily_requests:
            print("Exceeded daily request limit. Sleeping until tomorrow.")
            time.sleep(day_in_sec)
            total_requests_today = 0


def process_response(data):
    """
    Extract/process the data returned in the request to return the needed information.
    :param data: the JSON data of the request
    :return: list(duration, distance) of the particular trip.
    """
    try:
        if data["status"] != "OK":
            raise ValueError("Request status not OK")

        if data["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
            raise ZeroResultsError("No results found")

        duration = data["rows"][0]["elements"][0]["duration"]["value"]
        distance = data["rows"][0]["elements"][0]["distance"]["value"]

    except (KeyError, IndexError, ValueError) as e:
        raise ValueError("Exception: {}".format(e))

    return duration, distance


def save_to_db(route, details, duration, distance):
    """
    Save the route info to the DB. Search for existing DB entries first, and
    add to them if needed, otherwise generate new entries.
    :param route: string of the origin and destination, joined with a "_"
    :param details: dict of details about the trip - mode, what time, URL, etc.
    :param duration: time in seconds of the trip
    :param distance: distance in meters of the trip
    :return: none
    """
    origin, dest = route.split("_")
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

        t = Trip(mode = details["mode"],
                 time = details["hour"],
                 duration = duration,
                 distance = distance,
                 destination = d)
        d.trips.add(t)
