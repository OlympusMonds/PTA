Public Transport Analyser
=========================

This software is designed to see how much longer it takes to use public 
transport compared to driving.

The algorithm
-------------
The basic idea is that the program generates a random start location 
(the origin), and then 10 random end locations (the destination(s)). For
each route (from origin to destination), it asks Google for how long it
will take to drive, and then how long it will take using public 
transport at various times (currently: 6:00, 8:00, 12:00, 17:00, 21:00).

The ratio of time from driving to public transport is then calculated to
see how good or bad it is. After these 10 random destinations are done, 
a new origin is generated, and the process repeats. After some time, the
algorithm will revisit previous origins, and add more destinations to
provide better coverage. It runs at about 1000 m resolution at the 
moment, but will be increased.

The idea
--------
Hopefully the end product will be a website where someone can click on a
point on a map, and it will display a heat map of the surrounding city,
with the colours representing how good or bad the public transport 
system can service the route (compared to owning a car). This will 
hopefully be a tool the public and government can use to assess where 
new public transport upgrades should be targeted. It also may reveal 
certain biases, like if safe political seats get better or worse 
treatment in these sort of public services. This idea was partly 
inspired by [this](http://sydney.edu.au/news/84.html?newsstoryid=10504).

Current issues
--------------
To use Google's distance matrix API for free, it is limited to 2500 
requests a day. Currently each route takes 6 requests (1 driving, 5 
public transport times), and each origin gets 10 routes generated. This
means about 41 routes per day, which is pretty slow going. Oh well. 

Can I run this too?
-------------------
Yes, you just need to make a file in the src directory called "api.py",
and in there put your Google Maps Distance Matrix API key.


Dependencies
------------
For the server aspect (main.py), you need:

* arrow	0.7.0	0.7.0
* pony	0.6.5	0.6.5
* requests	2.9.1	2.9.1
* plus whatever they depend on
    
For the visualiser (visualise_routes.py), you need:

* pony	0.6.5	0.6.5
* matplotlib 
* plus whatever they depend on
    
The visualiser is pretty dodgey at the moment, just used for debugging.

Code analysis
-------------
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/26af7dbad1ab4ded84a340bbfe8e1927/badge.svg)](https://www.quantifiedcode.com/app/project/26af7dbad1ab4ded84a340bbfe8e1927)


Things to do
------------

* Batch requests to Google. Currently it's 1 request for 1 route, but
they support up to 100. Need to balance the time though.
* Fix up visualiser.
* Think about how to do web vis.