var map;

$(function() {
  /* Basic map configuration. */
  var initializeMap = function(center, zoom) {
    map = L.map('map', {
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
    map.heat = L.heatLayer([], {});
    map.addControl(map.heat);

    /* Ensure that changes are picked up when the user changes map options. */
    $('.heat-option input').on('change', updateHeatOptions).change();
    $('input[name="clusters"]').on('change', updateClusters).change();
  };

  /* Allow the user to set heat map options via form input. */
  var updateHeatOptions = function() {
    var options = {};
    $('.heat-option input').each(function(i, item) {
      var option = $(item);
      options[option.attr('name')] = parseFloat(option.val());
    });
    map.heat.setOptions(options);
  }

  /* Changing the cluster count will make another backend call for data. */
  var updateClusters = function() {
    $('#loading').show();
    getGeodata($(this).val());
  }

  /* Retrieve geojson data & display on the map. */
  var getGeodata = function(clusters) {
    $.getJSON($('#map').data('geodataUrl'), {
      'clusters': clusters
    }).done(function(data) {
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

  initializeMap([31.765537, -87.451171], 7);
});
