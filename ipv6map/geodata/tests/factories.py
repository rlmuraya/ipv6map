import datetime

import factory
import factory.fuzzy


class Version(factory.django.DjangoModelFactory):
    publish_date = factory.fuzzy.FuzzyDate(datetime.date(2010, 1, 1))
    is_active = True

    class Meta:
        model = 'geodata.Version'


class Location(factory.django.DjangoModelFactory):
    version = factory.SubFactory('ipv6map.tests.factories.Version')
    density = factory.fuzzy.FuzzyInteger(0, 2 ** 128 - 1)
    latitude = factory.fuzzy.FuzzyFloat(-90, 90)
    longitude = factory.fuzzy.FuzzyFloat(-90, 90)

    class Meta:
        model = 'geodata.Location'
