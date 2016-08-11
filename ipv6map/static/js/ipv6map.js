var map;

$(function() {
  /* Basic map configuration. */
  var initializeMap = function(container, center, zoom) {
    map = L.map(container[0], {
      center: center,
      zoom: zoom,
      fullscreenControl: {
        position: "topright"
      }
    });
    map.addControl(L.tileLayer(
      'http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png',
      {
        attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, ' +
                     '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
        minZoom: 2,
        noWrap: true  // prevent duplicated worlds
      }
    ));

    /* Configure the heatmap layer. */
    map.heat = L.heatLayer([], {radius: 9});
    map.addControl(map.heat);
  }

  /* Retrieve geojson data & display on the map. */
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

  /* Allow user to adjust heat map radius. */
  $('#increase-radius').click(function(e) {
    e.preventDefault();
    map.heat.setOptions({radius: Math.min(map.heat.options.radius + 1, 25)});
  });
  $('#reset-radius').click(function(e) {
    e.preventDefault();
    map.heat.setOptions({radius: 9});
  });
  $('#decrease-radius').click(function(e) {
    e.preventDefault();
    map.heat.setOptions({radius: Math.max(map.heat.options.radius - 1, 1)});
  });

  var container = $('#map');
  initializeMap(container, [31.765537, -87.451171], 6);
  getGeodata(container.data('geodataUrl'));
});
