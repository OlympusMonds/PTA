import requests
import time

def request_url(url):

    r = requests.get(url)

    if r.status_code == 200:
        return r.json()


def request_urls(urls):
    data = {}
    for url in urls:
        data[url] = request_url(url)
        time.sleep(0.4)

    return data