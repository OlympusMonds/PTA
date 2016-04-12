import requests
import time


def request_urls(url_queue):
    total_requests_today = 0

    while True:
        if total_requests_today >= 1500:
            print("Exceeded daily request limit. Sleeping until tomorrow.")
            time.sleep(3600*24)
            total_requests_today = 0

        route, details = url_queue.get()
        url = details["url"]

        print total_requests_today, url
        r = requests.get(url)

        if r.status_code == 200:
            print r.json()
        print
        time.sleep(0.1)

        url_queue.task_done()
        total_requests_today += 1

    return None
