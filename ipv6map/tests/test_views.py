from django.test import TestCase
from django.urls import reverse


class TestApp(TestCase):
    url_name = "app"
    template_name = "app.html"

    def test_get(self):
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
