var map;

$(function() {
  var initializeMap = function(container, center, zoom) {
    /* Basic map configuration. */
    map = L.map(container, {
      fullscreenControl: {
        position: "bottomleft"
      }
    });
    map.setView(center, zoom);
    map.addControl(L.tileLayer(
      'http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png',
      {
        attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, ' +
                     '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
        minZoom: 3,
      }
    ));

  }

  var getGeodata = function(url) {
    $.getJSON(url).done(function(data) {
      // TODO
    }).fail(function(xhr, status, error) {
      // TODO
    });
  }

  var container = $('#map');
  initializeMap(container[0], [35.875189, -78.842686], 12);
  getGeodata(container.data('geodataUrl'));
});
