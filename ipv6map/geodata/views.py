import logging

from django.http import JsonResponse
from django.views import View

from . import forms
from . import models


logger = logging.getLogger(__name__)


class LocationListAPI(View):

    def get(self, request, *args, **kwargs):
        version = models.Version.objects.get_current_version()
        if not version:
            error_msg = "Current version has not been configured."
            logger.error(error_msg)
            return JsonResponse({'error': error_msg}, status=404)

        form = forms.LocationFilter(data=self.request.GET)
        if not form.is_valid():
            return JsonResponse({
                'error': "Invalid boundary parameters.",
                'form_errors': form.errors,
            }, status=400)

        locations = version.location_set.filter(**form.get_filters())
        locations = [(float(l.latitude), float(l.longitude), int(l.density))
                     for l in locations]
        return JsonResponse({
            'version': version.publish_date.strftime('%Y-%m-%d'),
            'locations': locations,
        })
