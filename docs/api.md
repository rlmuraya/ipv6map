# Location/Density API

The location API is exposed at `/geodata/locations/`. This endpoint returns a
list of items of the format (latitude, longitude, density).

By default, data is returned for all locations associated with the current
version. Optionally, you can limit the number of results in one of two ways:

* **Bounding box.** Provide geographical boundaries via the `north`, `south`,
  `east`, and `west` parameters.

* **Clustering.** Group locations into *n* clusters, and sum the density for
  each cluster. Specify the number of clusters through the `clusters`
  parameter.
