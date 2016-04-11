import requests
import time

def request_url(url):

    r = requests.get(url)


def request_urls(urls):

    for url in urls:
        data = request_url(url)
        time.sleep(0.1)