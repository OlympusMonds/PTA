import time
import requests


def request_urls(max_daily_requests, bad_routes, url_queue, data_queue):
    """
    Request the route from Google at a steady pace that does not exceed the usage
    limits. If the data is OK, save it to the database.
    :param max_daily_requests: int of how many requests we're allowed to do per day.
    :param url_queue: The queue of URLs to process
    :return: None, the while loop should run forever.
    """

    total_requests_today = 0
    day_in_sec = 3600*24
    request_rate = day_in_sec / max_daily_requests

    while True:
        route_info = url_queue.get()
        print(total_requests_today, route_info["url"])

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

        if total_requests_today >= max_daily_requests:
            print("Exceeded daily request limit. Sleeping until tomorrow.")
            time.sleep(day_in_sec)  # TODO: This isn't what you want. You need to make this be "sleep for the rest of this day".
            total_requests_today = 0