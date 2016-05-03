bounding_boxes = {"CBD":
                      {"minlat": -33.846351, "minlon": 151.151910,
                       "maxlat": -33.938762, "maxlon": 151.254523,
                       "weight": 1,
                       "reuse_origins": True,
                       },
                  "North-western sydney":
                      {"minlat": -33.698758, "minlon": 150.832593,
                       "maxlat": -33.847816, "maxlon": 151.031604,
                       "weight": 1,
                       "reuse_origins": True,
                       },
                  "All Sydney":
                      {"minlat": -33.598618, "minlon": 150.750642,
                       "maxlat": -34.086191, "maxlon": 151.331951,
                       "weight": 2,
                       "reuse_origins": False,
                       },
                  }

map_resolution = 3  # About 1 km

max_daily_requests = 100000
requester_threads = 2

queue_size = 50  # If you make this too large, the times used can be in the past!
