import requests
import time
import pony.orm as pny
from database import Origin, Destination


def request_urls(url_queue, db):
    total_requests_today = 0
    day_in_sec = 3600*24
    max_daily_requests = 2500
    request_rate = day_in_sec / max_daily_requests

    while True:
        if total_requests_today >= max_daily_requests:
            print("Exceeded daily request limit. Sleeping until tomorrow.")
            time.sleep(day_in_sec)
            total_requests_today = 0

        route, details = url_queue.get()
        url = details["url"]

        print total_requests_today, url
        r = requests.get(url)

        if r.status_code == 200:
            duration, distance = process_response(r.json())

        origin, dest = route.split("_")
        with pny.db_session:
            if not Origin.exists(location = origin):
                o = Origin(location = origin)
            else:
                o = Origin.get(location = origin)

            d = Destination(location = dest,
                            mode = details["mode"],
                            time = details["hour"],
                            duration = duration,
                            distance = distance,
                            origin = o)

            o.destinations.add(d)

        time.sleep(request_rate)

        total_requests_today += 1
        url_queue.task_done()


def process_response(data):
    duration = -1
    distance = -1
    try:
        duration = data["rows"][0]["elements"][0]["duration"]["value"]
        distance = data["rows"][0]["elements"][0]["distance"]["value"]
    except (KeyError, IndexError):
        print("Error in processing response!")
        print(data)
        pass

    return duration, distance

