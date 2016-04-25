import sys
import queue
from threading import Thread

from public_transport_analyser.database.database import init
from public_transport_analyser.data_gatherer.route_generator import generate_routes
from public_transport_analyser.data_gatherer.url_requester import request_urls
from public_transport_analyser.data_gatherer.data_processor import process_data
from public_transport_analyser.data_gatherer.config import bounding_box, map_resolution, max_daily_requests, queue_size, requester_threads


def main():

    url_queue = queue.Queue(maxsize=queue_size)
    data_queue = queue.Queue(maxsize=queue_size*10)

    db = init()

    bad_routes = set()

    # TODO: Migrate the route thread into a simple function call within the url thread.
    route_thread = Thread(target=generate_routes, args=(bounding_box, map_resolution, url_queue,))
    route_thread.start()

    for t in range(requester_threads):
        url_request_thread = Thread(target=request_urls, args=(max_daily_requests/float(requester_threads), bad_routes, url_queue, data_queue))
        url_request_thread.start()

    data_processing_thread = Thread(target=process_data, args=(bad_routes, data_queue,))
    data_processing_thread.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())






