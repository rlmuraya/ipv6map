from django.db import models


class VersionManager(models.Manager):

    def get_current_version(self):
        """Return the current version of data that we'll display to users."""
        return self.filter(is_active=True).first()


class Version(models.Model):
    """A date that the source published geodata.

    By associating data with a version, and managing its status, we can
    update data behind the scenes and avoid showing users incomplete or old
    data.
    """
    # At time of writing, data is published once a month on the first Tuesday.
    publish_date = models.DateField(
        help_text="Date the data was published by the source.")
    is_active = models.BooleanField(default=False)

    objects = VersionManager()

    class Meta(object):
        # The most recently created instance of the most recent publication date.
        # will be returned first.
        ordering = ['-publish_date', '-id']

    def __str__(self):
        return "{} ({})".format(
            self.publish_date.strftime('%Y-%m-%d'),
            "active" if self.is_active else "inactive")

    def activate(self):
        """Set this version to the current, active version."""
        self.is_active = True
        self.save()
        Version.objects.exclude(pk=self.pk).update(is_active=False)


class Location(models.Model):
    """Represent the IPV6 address density at a geographical location."""
    version = models.ForeignKey('geodata.Version', on_delete=models.CASCADE)

    # Django's BigIntegerField stores values up to (2 ** 63 - 1).
    # However there are 2 ** 128 possible IPv6 addresses and some locations
    # have more addresses than BigIntegerField can handle.
    density = models.DecimalField(
        max_digits=39,  # len(str(2 ** 128)) -> 39
        decimal_places=0,
        help_text="Count of IPV6 addresses at this location.")

    # At time of writing, the data source provides latitude and longitude
    # values to 4 decimal places of precision, though it is common for data
    # sources to provide up to 6 decimal fields of precision.
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta(object):
        unique_together = [
            ('version', 'latitude', 'longitude'),
        ]

    def __str__(self):
        return "({}, {}) has {} IPV6 addresses (updated {})".format(
            self.latitude,
            self.longitude,
            self.density,
            self.version.publish_date.strftime('%Y-%m-%d'),
        )
