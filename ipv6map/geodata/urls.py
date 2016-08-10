from django.conf.urls import url

from . import views


app_name = "geodata"

urlpatterns = [
    url(r'^geodata/locations/$',
        views.LocationListAPI.as_view(),
        name='api-location-list'),
]
