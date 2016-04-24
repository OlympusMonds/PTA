import arrow
import api


def get_url(origin, destination, mode, time):
    units = "metric"
    apikey= api.apikey

    url = "https://maps.googleapis.com/maps/api/distancematrix/json?" \
          "&units={units}" \
          "&origins={origins}" \
          "&destinations={destinations}" \
          "&mode={mode}" \
          "&departure_time={time}" \
          "&key={apikey}".format(units=units,
                                 origins=origin,  # Note the plural change
                                 destinations=destination,
                                 mode=mode,
                                 time=time,
                                 apikey=apikey)

    return url


def convert_hour_to_epoch(hour):
    """
    We always need to look up times in the future, so the time is always set
    for tomorrow. Time is floored to the hour, and then set
    :param: an int for the hour of the day in 24hr time.
    :return: time in seconds from epoch to tomorrow at that hour's time.
    """
    return arrow.now()\
                .floor('hour')\
                .replace(days=+1, hour=hour)\
                .to('utc')\
                .timestamp


def get_info_for_route(route):
    """

    :param route: string that looks like "<origin>_<destination>", where both
    origin and destination look like "<lat>,<lon>".
    :return:
    """
    origin, destination = route.split("_")

    modes = ["transit", "driving"]
    hours = [6, 8, 12, 17, 21]

    route_info = []

    for mode in modes:
        for hour in hours:
            route_info.append({"route": route,
                               "url": get_url(origin, destination, mode, convert_hour_to_epoch(hour)),
                               "mode": mode,
                               "hour": hour})

            if mode == "driving":
                break  # looks like asking for driving times in the future makes no difference

    return route_info
