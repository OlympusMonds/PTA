import time
import datetime
import requests
import logging


def request_urls(max_daily_requests, bad_routes, url_queue, data_queue):
    """
    Request the route from Google at a steady pace that does not exceed the usage
    limits. If the data is OK, save it to the database.
    :param max_daily_requests: int of how many requests we're allowed to do per day.
    :param url_queue: The queue of URLs to process
    :return: None, the while loop should run forever.
    """
    logger = logging.getLogger('PTA.request_urls')

    day_in_sec = 3600.*24.
    request_rate = day_in_sec / max_daily_requests

    total_requests_today = 0
    start_time = datetime.datetime.now()
    logger.debug("start_time = {}".format(start_time))

    while True:
        logger.debug("Getting route_info")
        route_info = url_queue.get()
        logger.debug("Got route_info")

        logger.info("Req {0}: route = {1}, url = {2}".format(total_requests_today,
                                                              route_info["route"],
                                                              route_info["url"]))
        logger.debug("Request sleep period = {}".format(request_rate))

        need_to_sleep = True

        if route_info["route"] not in bad_routes:
            try:
                logger.debug("Requesting data for route {}".format(route_info["route"]))
                r = requests.get(route_info["url"])
                logger.debug("Got data for route {}".format(route_info["route"]))

                if r.status_code == 200:
                    reqjson = r.json()

                    if reqjson["status"] == "OK":
                        data_queue.put((route_info, reqjson))

                    elif reqjson["status"] == "OVER_QUERY_LIMIT":
                        total_requests_today = max_daily_requests + 1  # we need to stop now
                        logger.error("Google says limit has been reached")
                    else:
                        logger.error("Unknown response status: {0}; skipped".format(reqjson["status"]))
                else:
                    logger.error("Bad response (response = {0}); skipped.".format(r.status_code))

            except ConnectionError as ce:
                logger.error("Connection error. Computer says:\n{0}".format(ce))
                need_to_sleep = False
            except Exception as e:
                logger.error("Unknown exception caught. Computer says:\n{0}\nskipped.".format(e))

        else:
            logger.info("Bad route {}; skipped.".format(route_info["route"]))
            need_to_sleep = False

        url_queue.task_done()
        logger.debug("Queued route {} released.".format(route_info["route"]))

        if need_to_sleep:
            logger.debug("Sleeping for {} seconds".format(request_rate))
            total_requests_today += 1
            time.sleep(request_rate)

        time_passed = (datetime.datetime.now() - start_time).total_seconds()
        if not total_requests_today == max_daily_requests:
            request_rate = (day_in_sec - time_passed) / (max_daily_requests - total_requests_today)
        logger.debug("Time passed today: {} seconds, request_rate: {} seconds".format(time_passed, request_rate))

        if time_passed >= day_in_sec:
            logger.info("24 hours passed. Resetting count to new day.")
            total_requests_today = 0
            request_rate = day_in_sec / max_daily_requests
            start_time = datetime.datetime.now()

        if total_requests_today >= max_daily_requests:
            seconds_until_tomorrow = day_in_sec - time_passed
            logger.error("Exceeded daily request limit. Sleeping until tomorrow (for {} seconds).".format(seconds_until_tomorrow))
            total_requests_today = 0
            time.sleep(seconds_until_tomorrow)

        logger.debug("Finished with route {}".format(route_info["route"]))