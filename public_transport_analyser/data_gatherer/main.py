import sys
import queue
from threading import Thread
import logging

from public_transport_analyser.database.database import init
from public_transport_analyser.data_gatherer.route_generator import generate_routes
from public_transport_analyser.data_gatherer.url_requester import request_urls
from public_transport_analyser.data_gatherer.data_processor import process_data
from public_transport_analyser.data_gatherer.config import \
    bounding_boxes, map_resolution, max_daily_requests, queue_size, requester_threads


def setup_logging(log_to_file = True):
    logger = logging.getLogger('PTA')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if log_to_file:
        fh = logging.FileHandler('pta.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def main():
    logger = setup_logging(log_to_file=False)

    url_queue = queue.Queue(maxsize=queue_size)
    data_queue = queue.Queue(maxsize=queue_size)

    db = init()

    bad_routes = set()

    logger.info("Create route generating threads")
    for name, bb in bounding_boxes.items():
        for i in range(int(bb["weight"])):
            tname = "{name} {index}".format(name=name, index=i)
            route_thread = Thread(target=generate_routes, args=(tname, bb, map_resolution,
                                                                bb["reuse_origins"], url_queue,))
            route_thread.start()
    logger.info("Created route generating threads")

    logger.info("Create url requesting threads")
    for _ in range(requester_threads):
        url_request_thread = Thread(target=request_urls, args=(max_daily_requests/float(requester_threads),
                                                               bad_routes, url_queue, data_queue))
        url_request_thread.start()
    logger.info("Created url requesting threads")

    logger.info("Create data processing thread")
    data_processing_thread = Thread(target=process_data, args=(bad_routes, data_queue,))
    data_processing_thread.start()
    logger.info("Created data processing thread")


    return 0


if __name__ == "__main__":
    sys.exit(main())






