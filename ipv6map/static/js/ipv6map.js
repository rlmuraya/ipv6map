var map;

$(function() {
  var InfoBox = L.Control.extend({
    options: {
      position: "topright"
    },
    onAdd: function(map) {
      this._container = L.DomUtil.create('div', 'info');
      this.welcome();
      return this._container;
    },
    welcome: function() {
      var container = $(this._container);
      container.empty()
      container.append("<h3>Hello</h3>");
    }
  });

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

    /* Configure info box. */
    map.info = new InfoBox()
    map.addControl(map.info);
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
