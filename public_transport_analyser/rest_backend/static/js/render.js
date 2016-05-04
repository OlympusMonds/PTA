/**
 * Created by luke on 4/05/16.
 */

var map;
var origins;

function rgbToHex(r, g, b) {
    // http://stackoverflow.com/a/5624139
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function clearMap() {
    map.data.forEach(function (feature) {
        map.data.remove(feature);
    });
}

function showOrigins() {
    map.data.addGeoJson(origins);
}

function loadGeoJson(url, options) {
    var promise = new Promise(function (resolve, reject) {
        try {
            map.data.loadGeoJson(url, options, function (features) {
                resolve(features);
            });
        } catch (e) {
            reject(e);
        }
    });
    return promise;
}


function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 11,
        center: {lat: -33.9, lng: 151.2}
    });

    // Load GeoJSON
    var promise = loadGeoJson('/api/origins');
    promise.then(function (features) {
        document.getElementById('info').textContent = "Loading succeeded. Click on a flag.";
        map.data.toGeoJson(function (data) {
            origins = data;  // cache data
        });
    });
    promise.catch(function (error) {
        document.getElementById('info').textContent = "Loading failed";
    });


    map.data.setStyle(function(feature) {
        var origin_image = {
            url: '/static/imgs/origin.png',
            size: new google.maps.Size(20, 32),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(0, 32)
        };
        var dest_image = {
            url: '/static/imgs/destination.png',
            size: new google.maps.Size(20, 32),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(0, 32)
        };

        if (feature.getProperty('isOrigin')) {
            return /** @type {google.maps.Data.StyleOptions} */({
                icon: origin_image,
            });
        }
        else if (feature.getProperty('isPolygon')) {
            var ratiocolour;
            var ratio = feature.getProperty('ratio');
            var opacity = 0.4;
            
            if (ratio <= 1.0) {
                ratiocolour = rgbToHex(255, Math.round(ratio*255), Math.round(ratio*255));
                opacity = 0.2 + (0.4 * (1.-ratio));
            }
            else {
                ratio = 2.0;
                ratiocolour = rgbToHex(Math.round((1-(ratio-1.))*255), Math.round((1-(ratio-1.))*255), 255);
                opacity = 0.2 + (0.4 * (1-(ratio-1.)));
            }

            return /** @type {google.maps.Data.StyleOptions} */({
                fillColor: ratiocolour,
                strokeWeight: 1,
                fillOpacity: opacity,
            });
        }
        else if (feature.getProperty('isDestination')) {
            return /** @type {google.maps.Data.StyleOptions} */({
                icon: dest_image,
            });
        }
    });


    // Set mouseover event for each feature.
    map.data.addListener('mouseover', function(event) {
        var content = "";
        if (event.feature.getProperty('isOrigin')) {
            content = "Location: " + event.feature.getProperty('location') +
                    "; Destinations: " + event.feature.getProperty('num_dest');
        }
        else if (event.feature.getProperty('isPolygon')) {
            var ratio = event.feature.getProperty('ratio');
            if (ratio == -1) {
                content = "No data available."
            }
            else if (ratio < 1) {
                content = "It is " + (1.0/ratio).toFixed(2) + " times slower to catch public transport than to drive";
            }
            else {
                content = "It is " + (1.0/ratio).toFixed(2) + " times faster to catch public transport than to drive";
            }
        }
        else if (event.feature.getProperty('isDestination')) {
            content = "Destination coordinates: " + event.feature.getProperty('location');
        }
        document.getElementById('info').textContent = content;
    });


    map.data.addListener('click', function(event) {
        clearMap();

        if (event.feature.getProperty('isOrigin')) {
            origin = event.feature.getProperty('location');

            // Load GeoJSON
            var promise = loadGeoJson('/api/origin/' + origin);
            promise.then(function (features) {
                //document.getElementById('info').textContent = "Loading succeeded. Click on a flag to begin.";
            });
            promise.catch(function (error) {
                document.getElementById('info').textContent = "Loading failed";
            });
        }
        else {
            showOrigins();
        }
    });

}