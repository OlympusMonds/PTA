/**
 * Created by luke on 4/05/16.
 */

// Make time slider
$(function() {
    var select = $( "#daytime" );
    var slider = $( "<div id='slider'></div>" ).insertAfter( select ).slider({
      min: 1,
      max: 5,
      range: "min",
      value: select[ 0 ].selectedIndex + 1,
      slide: function( event, ui ) {
        select[ 0 ].selectedIndex = ui.value - 1;
        time = $('#daytime option:selected').text();
      }
    });
    $( "#daytime" ).change(function() {
        slider.slider( "value", this.selectedIndex + 1 );
        time = $('#daytime option:selected').text();
    });
  });


var map;
var origins;
var time = 6;


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


function ratioText(ratio){
    if (ratio == -1) {
        return "No data available."
    }
    else if (ratio < 1) {
        return "It is " + (1.0/ratio).toFixed(2) + " times slower to catch public transport than to drive";
    }
    else {
        return "It is " + ratio.toFixed(2) + " times faster to catch public transport than to drive";
    }
}


function avgRatioText(ratio){
    if (ratio == -1) {
        return "No data available."
    }
    else if (ratio < 1) {
        return "It is on average " + (1.0/ratio).toFixed(2) + " times slower to catch public transport from here than to drive";
    }
    else {
        return "It is on average " + ratio.toFixed(2) + " times faster to catch public transport from here than to drive";
    }
}


function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 11,
        center: {lat: -33.9, lng: 151.2},
        mapTypeControl: false,
        streetViewControl: false,
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
        else if (feature.getProperty('isOPoly')) {
            var ratiocolour;
            var ratio = feature.getProperty('ratio');
            var opacity = 0.4;

            if (ratio == -1) {
                ratiocolour = rgbToHex(0, 0, 0);
                opacity = 0.6;
            }
            else if (ratio <= 1.0) {
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
                strokeOpacity: 0.05,
                fillOpacity: opacity,
            });
        }
        else if (feature.getProperty('isPolygon')) {
            var ratiocolour;
            var ratio = feature.getProperty('ratio');
            var opacity = 0.4;
            
            if (ratio == -1) {
                ratiocolour = rgbToHex(0, 0, 0);
                opacity = 0.6;
            }
            else if (ratio <= 1.0) {
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
                strokeOpacity: 0.05,
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
            content = "Start coordinates: " + event.feature.getProperty('location');
        }
        else if (event.feature.getProperty('isPolygon')) {
            content = ratioText(event.feature.getProperty('ratio'));
        }
        else if (event.feature.getProperty('isOPoly')) {
            content = avgRatioText(event.feature.getProperty('ratio'));
        }
        else if (event.feature.getProperty('isDestination')) {
            content = ratioText(event.feature.getProperty('ratio')) +
                      ". Destination coordinates: " + event.feature.getProperty('location');
        }
        document.getElementById('info').textContent = content;
    });


    map.data.addListener('click', function(event) {
        clearMap();

        if (event.feature.getProperty('isOrigin')) {
            origin = event.feature.getProperty('location');

            // Load GeoJSON
            var promise = loadGeoJson('/api/origin/' + origin + '/' + time);
            promise.then(function (features) {
                //document.getElementById('info').textContent = "Loading succeeded. Click on a flag to begin.";
            });
            promise.catch(function (error) {
                document.getElementById('info').textContent = "Loading failed";
            });
        }
        else if (event.feature.getProperty('isOPoly')) {
            origin = event.feature.getProperty('location');

            // Load GeoJSON
            var promise = loadGeoJson('/api/origin/' + origin + '/' + time);
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