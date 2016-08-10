import datetime
import json

from django.test import TestCase
from django.urls import reverse

from ipv6map.tests import factories


class TestLocationListAPI(TestCase):
    url_name = "geodata:api-location-list"

    def test_current_version_not_configured(self):
        """Should get 404 response when no current Version is available."""
        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'error': "Current version has not been configured.",
        })

    def test_no_locations(self):
        """Should get Version date & empty locations list if there are no locations."""
        version = factories.Version()

        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf8"))
        self.assertEqual(data, {
            'version': version.publish_date.strftime("%Y-%m-%d"),
            'locations': [],
        })

    def test_get(self):
        """Data should be returned as a JSON-encoded summary."""
        version = factories.Version(publish_date=datetime.date(2016, 8, 2))
        other_version = factories.Version(is_active=False)
        for i in range(3):
            factories.Location(
                version=version, latitude=i, longitude=i, density=i)
            factories.Location(
                version=other_version, latitude=-i, longitude=-i, density=i + 10)

        response = self.client.get(reverse(self.url_name))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data, {
            'version': "2016-08-02",
            'locations': [
                [0.0, 0.0, 0],
                [1.0, 1.0, 1],
                [2.0, 2.0, 2],
            ],
        })
