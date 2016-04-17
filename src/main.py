import sys
from url_requester import request_urls
from route_generator import generate_routes
from database import init

from Queue import Queue
from threading import Thread


def main():
    url_queue = Queue(maxsize=10)   # If you make this too large, the times used can be
                                    # in the past!
    db = init()

    # Why did I make these things both threaded? It works, but it just seems unneeded
    # now... Particularly the route thread - why couldn't the url request thread just
    # call for a route just before it requests? Having the request threaded is OK,
    # particularly if I get more than 1 API key.
    route_thread = Thread(target=generate_routes, args=(url_queue,))
    url_request_thread = Thread(target=request_urls, args=(url_queue,))

    route_thread.start()
    url_request_thread.start()

    print "All threads go!"

    return 0


if __name__ == "__main__":
    sys.exit(main())






