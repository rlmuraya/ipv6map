from decimal import Decimal

from django.test import TestCase

from .. import forms


class TestLocationFilter(TestCase):

    def setUp(self):
        super().setUp()

    def test_minimum(self):
        """All fields ensure that their value is above -90."""
        data = {d: -100 for d in ('north', 'south', 'east', 'west')}
        form = forms.LocationFilter(data=data)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(dict(form.errors), {
            'north': ['Ensure this value is greater than or equal to -90.'],
            'south': ['Ensure this value is greater than or equal to -90.'],
            'east': ['Ensure this value is greater than or equal to -90.'],
            'west': ['Ensure this value is greater than or equal to -90.'],
        })
        self.assertIsNone(form.get_filters())

    def test_maximium(self):
        """All fields ensure that their value is less than 90."""
        data = {d: 100 for d in ('north', 'south', 'east', 'west')}
        form = forms.LocationFilter(data=data)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(dict(form.errors), {
            'north': ['Ensure this value is less than or equal to 90.'],
            'south': ['Ensure this value is less than or equal to 90.'],
            'east': ['Ensure this value is less than or equal to 90.'],
            'west': ['Ensure this value is less than or equal to 90.'],
        })
        self.assertIsNone(form.get_filters())

    def test_valid__all_boundaries(self):
        """Form transforms boundaries to latitude/longitude query filters."""
        data = {
            'north': 36.35,
            'south': 34,
            'east': -75.5,
            'west': -84.25,
        }
        form = forms.LocationFilter(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertDictEqual(form.get_filters(), {
            'latitude__gte': Decimal('34'),
            'latitude__lte': Decimal('36.35'),
            'longitude__gte': Decimal('-84.25'),
            'longitude__lte': Decimal('-75.5'),
        })

    def test_valid__no_boundaries(self):
        """Form does not require any boundaries."""
        form = forms.LocationFilter(data={})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertDictEqual(form.get_filters(), {})

    def test_valid__partial_boundaries(self):
        """Form does not require that all boundaries are provided."""
        data = {
            'north': 36.35,
            'south': 34,
        }
        form = forms.LocationFilter(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertDictEqual(form.get_filters(), {
            'latitude__gte': Decimal('34'),
            'latitude__lte': Decimal('36.35'),
        })
