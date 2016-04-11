import requests
from url_generator import get_urls

def main():
    origins = "-33.9042051,151.2483879"
    destinations = "-33.9115947,151.2301782"

    urls = get_urls(origins, destinations)

    print '\n'.join(urls)


if __name__ == "__main__":
    main()