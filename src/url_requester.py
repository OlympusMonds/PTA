import requests
import time


def request_urls(url_queue):
    while True:
        route, details = url_queue.get()
        url = details["url"]

        r = requests.get(url)

        if r.status_code == 200:
            print r.json()

        time.sleep(0.1)

        url_queue.task_done()

    return None
