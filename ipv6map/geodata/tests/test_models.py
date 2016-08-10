import datetime
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from ipv6map.tests import factories

from .. import models


class TestVersionManager(TestCase):

    def test_get_current_version__no_versions(self):
        """Should return None if there are no Versions in the database."""
        self.assertIsNone(models.Version.objects.get_current_version())

    def test_get_current_version__all_inactive(self):
        """Should return None if only inactive Versions are in the database."""
        factories.Version(is_active=False)
        self.assertIsNone(models.Version.objects.get_current_version())

    def test_get_current_version(self):
        """Should return the active Version with the most recent publish_date.

        Most recently added objects should be preferred.
        """
        date = datetime.date(2016, 8, 2)
        version1 = factories.Version(publish_date=date, is_active=True)

        with self.subTest("Version should be considered current while it is "
                          "the only one in the database."):
            self.assertEqual(models.Version.objects.get_current_version(), version1)

        earlier_date = date - datetime.timedelta(days=3)
        version2 = factories.Version(publish_date=earlier_date, is_active=True)  # noqa
        with self.subTest("Version should still be considered current if an "
                          "active version is added for an earlier date."):
            self.assertEqual(models.Version.objects.get_current_version(), version1)

        later_date = date + datetime.timedelta(days=3)
        version3 = factories.Version(publish_date=later_date, is_active=False)  # noqa
        with self.subTest("Version should still be considered current if an "
                          "inactive version is added for a more recent date."):
            self.assertEqual(models.Version.objects.get_current_version(), version1)

        version4 = factories.Version(publish_date=date, is_active=True)
        with self.subTest("Version should no longer be considered current if "
                          "another version is added for the same date."):
            self.assertEqual(models.Version.objects.get_current_version(), version4)

        version5 = factories.Version(publish_date=later_date, is_active=True)
        with self.subTest("Version should no longer be considered current if "
                          "an active version is added for a more recent date."):
            self.assertEqual(models.Version.objects.get_current_version(), version5)


class TestVersionModel(TestCase):

    def test_str(self):
        """Smoke test for string representation."""
        with self.subTest(is_active=True):
            obj = factories.Version(publish_date=datetime.date(2016, 8, 2), is_active=True)
            self.assertEqual(str(obj), "2016-08-02 (active)")

        with self.subTest(is_active=False):
            obj = factories.Version(publish_date=datetime.date(2016, 8, 2), is_active=False)
            self.assertEqual(str(obj), "2016-08-02 (inactive)")

    def test_is_active_default(self):
        """Test that Version is created as inactive by default."""
        # Temporarily delete the is_active value defined by the factory, if any.
        orig_is_active = factories.Version._meta.declarations.pop('is_active', None)
        try:
            self.assertEqual(factories.Version().is_active, False)
        finally:
            if orig_is_active is not None:
                factories.Version._meta.declarations['is_active'] = orig_is_active

    def test_activate(self):
        """Activating a Version should deactivate all other active versions."""
        old_version1 = factories.Version(is_active=True)
        old_version2 = factories.Version(is_active=False)
        version = factories.Version(is_active=False)

        version.activate()

        old_version1.refresh_from_db()
        old_version2.refresh_from_db()
        version.refresh_from_db()
        self.assertTrue(version.is_active)
        self.assertFalse(old_version1.is_active)
        self.assertFalse(old_version2.is_active)


class TestLocationModel(TestCase):

    def test_str(self):
        """Smoke test for string representation."""
        location = factories.Location(
            latitude=Decimal('35.875189'),
            longitude=Decimal('-78.842686'),
            version__publish_date=datetime.date(2016, 8, 2),
            density=1000)
        self.assertEqual(
            str(location),
            "(35.875189, -78.842686) has 1000 IPV6 addresses (updated 2016-08-02)")

    def test_lat_lng_precision(self):
        """Model should truncate lat/lng if precision is too high."""
        location = factories.Location(
            latitude=Decimal('35.8751892'),
            longitude=Decimal('-78.8426864'))
        location.refresh_from_db()
        self.assertEqual(location.latitude, Decimal('35.875189'))
        self.assertEqual(location.longitude, Decimal('-78.842686'))

    def test_version_and_point_unique_together(self):
        """lat/lng must be unique to the Version the Location is associated with."""
        obj = factories.Location()
        with self.assertRaises(IntegrityError):
            factories.Location(
                version=obj.version, latitude=obj.latitude,
                longitude=obj.longitude)
