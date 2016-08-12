import logging

import pandas as pd

from scipy.cluster.vq import kmeans2

from django.http import JsonResponse
from django.views import View

from . import forms
from . import models


logger = logging.getLogger(__name__)


class LocationListAPI(View):

    def get(self, request, *args, **kwargs):
        """Summarize IPv6 density per location using the current API data.

        Limit locations to a geographical region by passing in "north",
        "south", "east", and "west" boundaries. Reduce the size of the data
        by specifying a number of clusters.
        """
        # Find the current version of API data.
        self.version = models.Version.objects.get_current_version()
        if not self.version:
            error_msg = "Current version has not been configured."
            logger.error(error_msg)
            return JsonResponse({'error': error_msg}, status=404)

        # Allow filtering locations by geographical bounds.
        form = forms.LocationFilter(data=self.request.GET)
        if not form.is_valid():
            return JsonResponse({
                'error': "Invalid boundary parameters.",
                'form_errors': form.errors,
            }, status=400)

        # Find the location objects we're interested in.
        locations = self.version.location_set.filter(**form.get_filters())
        locations = locations.values_list('latitude', 'longitude', 'density')
        locations = [(float(lat), float(lng), int(n)) for lat, lng, n in locations]

        num_clusters = form.cleaned_data.get('clusters')
        if num_clusters:
            # Group lat/lng values into geographical groups.
            df = pd.DataFrame(locations, columns=['lat', 'lng', 'density'])
            coordinates, indices = kmeans2(df[['lat', 'lng']], num_clusters)

            # Sum the density per group.
            result = [pd.DataFrame(indices, columns=['coord']), df[['density']]]
            result = pd.concat(result, axis=1)
            result = result.groupby('coord').sum()

            # (lat, lng, total_density) for each clustered lat, lng
            summaries = [list(coordinates[i]) + [total_density]
                         for i, total_density in result.to_dict()['density'].items()]

        else:
            summaries = locations

        return JsonResponse({
            'version': self.version.publish_date.strftime('%Y-%m-%d'),
            'locations': summaries,
        })
