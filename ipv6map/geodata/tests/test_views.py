import datetime
import json

from django.test import TestCase
from django.urls import reverse

from ipv6map.tests import factories


class TestLocationListAPI(TestCase):
    url_name = "geodata:api-location-list"

    def setUp(self):
        super().setUp()
        self.version = factories.Version(publish_date=datetime.date(2016, 8, 2))
        self.loc1 = factories.Location(
            version=self.version, latitude=1, longitude=1, density=1)
        self.loc2 = factories.Location(
            version=self.version, latitude=2, longitude=2, density=2)

    def test_current_version_not_configured(self):
        """Should get 404 response when no current Version is available."""
        self.version.delete()

        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'error': "Current version has not been configured.",
        })

    def test_no_locations(self):
        """Should get Version date & empty locations list if there are no locations."""
        self.version.location_set.all().delete()

        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'version': "2016-08-02",
            'locations': [],
        })

    def test_get(self):
        """Data should be returned as a JSON-encoded summary."""
        # Never include results from other versions.
        other_version = factories.Version(is_active=False)
        factories.Location(
            version=other_version, latitude=3, longitude=3, density=3)

        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'version': "2016-08-02",
            'locations': [
                [1.0, 1.0, 1],
                [2.0, 2.0, 2],
            ],
        })

    def test_filter(self):
        """Passing in boundaries should restrict the number of results returned."""
        boundaries = {'north': '1.5'}

        response = self.client.get(reverse(self.url_name), data=boundaries)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'version': "2016-08-02",
            'locations': [
                [1.0, 1.0, 1],
            ],
        })

    def test_filter__invalid(self):
        """Return a 400 response if user provides invalid filter parameters."""
        boundaries = {'north': 'invalid'}

        response = self.client.get(reverse(self.url_name), data=boundaries)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'error': "Invalid boundary parameters.",
            'form_errors': {
                'north': ["Enter a number."],
            },
        })
