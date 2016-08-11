var map;

$(function() {
  var initializeMap = function(container, center, zoom) {
    /* Basic map configuration. */
    map = L.map(container, {
      fullscreenControl: {
        position: "topright"
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

    /* Configure the heatmap layer. */
    map.heat = L.heatLayer([], {});
    map.addControl(map.heat);
  }

  var getGeodata = function(url) {
    $.getJSON(url).done(function(data) {
      /* Add the locations data to the map. */
      map.heat.setLatLngs(data.locations);

      /* Display when this data was last updated. */
      var version = new Date(data['version']);
      $("#version").html("Data retrieved on " + version.toDateString() + ".");

    }).fail(function(xhr, status, error) {
      /* Display error information in the info strip. */
      var info = $("#info");
      info.addClass('error');
      info.find("p").html(
        "An error occurred while retrieving the data:<br>" +
        xhr.status + " - " + (xhr.responseJSON ? xhr.responseJSON.error : error));
    }).always(function() {
      /* Remove the loading screen. */
      $("#loading").hide();
    });
  }

  var container = $('#map');
  initializeMap(container[0], [35.875189, -78.842686], 12);
  getGeodata(container.data('geodataUrl'));
});
