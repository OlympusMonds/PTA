import sys
import queue
from threading import Thread

from public_transport_analyser.database.database import init
from route_generator import generate_routes
from url_requester import request_urls
from config import bounding_box, map_resolution, max_daily_requests


def main():

    url_queue = queue.Queue(maxsize=10)   # If you make this too large, the times used can be in the past!

    db = init()

    # Why did I make these things both threaded? It works, but it just seems unneeded
    # now... Particularly the route thread - why couldn't the url request thread just
    # call for a route just before it requests? Having the request threaded is OK,
    # particularly if I get more than 1 API key.
    route_thread = Thread(target=generate_routes, args=(bounding_box, map_resolution, url_queue,))
    url_request_thread = Thread(target=request_urls, args=(max_daily_requests, url_queue,))

    # TODO: Implement logging
    print("Starting threads... ", end="")
    route_thread.start()
    url_request_thread.start()
    print("done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())






