import sys
from url_requester import request_urls
from route_generator import generate_routes

from Queue import Queue
from threading import Thread

def main():
    url_queue = Queue(maxsize=1000)

    route_thread = Thread(target=generate_routes, args=(url_queue,))
    url_request_thread = Thread(target=request_urls, args=(url_queue,))

    route_thread.start()
    url_request_thread.start()

    print "All threads go!"

    return 0


if __name__ == "__main__":
    sys.exit(main())






