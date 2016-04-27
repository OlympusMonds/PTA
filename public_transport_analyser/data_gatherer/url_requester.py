import time
import datetime
import requests


def request_urls(max_daily_requests, bad_routes, url_queue, data_queue):
    """
    Request the route from Google at a steady pace that does not exceed the usage
    limits. If the data is OK, save it to the database.
    :param max_daily_requests: int of how many requests we're allowed to do per day.
    :param url_queue: The queue of URLs to process
    :return: None, the while loop should run forever.
    """

    day_in_sec = 3600.*24.
    request_rate = day_in_sec / max_daily_requests

    total_requests_today = 0
    start_time = datetime.datetime.now()

    while True:
        route_info = url_queue.get()
        print("req {0}: route = {1}, reqrate = {2:0.3f}, url = {3}".format(total_requests_today,
                                                                           route_info["route"],
                                                                           request_rate,
                                                                           route_info["url"]))
        need_to_sleep = True

        if route_info["route"] not in bad_routes:
            try:
                r = requests.get(route_info["url"])
                if r.status_code == 200:
                    reqjson = r.json()

                    if reqjson["status"] == "OK":
                        data_queue.put((route_info, reqjson))

                    elif reqjson["status"] == "OVER_QUERY_LIMIT":
                        total_requests_today = max_daily_requests + 1  # we need to stop now
                        print("Google says limit has been reached")
                    else:
                        print("Unknown response status: {0}; skipped".format(reqjson["status"]))
                else:
                    print("Bad response (response = {0}); skipped.".format(r.status_code))

            except ConnectionError as ce:
                print("Connection error. Computer says:\n{0}".format(ce))
                need_to_sleep = False
            except Exception as e:
                print("Unknown exception caught. Computer says:\n{0}\nskipped.".format(e))

        else:
            print("Bad route; skipped.")
            need_to_sleep = False

        url_queue.task_done()

        if need_to_sleep:
            total_requests_today += 1
            time.sleep(request_rate)

        time_passed = (datetime.datetime.now() - start_time).total_seconds()
        request_rate = (day_in_sec - time_passed) / (max_daily_requests - total_requests_today)

        if time_passed >= day_in_sec:
            print("24 hours passed. Resetting count to new day.")
            total_requests_today = 0
            start_time = datetime.datetime.now()

        if total_requests_today >= max_daily_requests:
            print("Exceeded daily request limit. Sleeping until tomorrow.")
            total_requests_today = 0
            time.sleep(day_in_sec - time_passed)
