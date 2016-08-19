import datetime
import ipaddress
import logging
import os
import re

import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ipv6map.geodata import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync geodata tables with the most recently downloaded IPV6 data."

    GEODATA_REGEX = re.compile(
        r'^GeoLite2-City-CSV_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})$')

    def add_arguments(self, parser):
        # Normally we skip loading data that has already been loaded.
        parser.add_argument(
            '--force-create',
            action='store_true',
            dest='force_create',
            default=False,
            help="Force geodata to be loaded, even if a Version already "
                 "exists for the most recent publication date.")
        return parser

    @transaction.atomic
    def handle(self, force_create=False, *args, **kwargs):
        publish_date = self.get_last_publication_date()

        # Don't create a duplicate version unless specified by the caller.
        if not force_create:
            if models.Version.objects.filter(publish_date=publish_date).exists():
                logger.info(
                    "Version data for {} has already been loaded. "
                    "To load again anyway, run this command with the "
                    "--force-create flag.".format(publish_date.strftime("%Y-%m-%d")))
                return

        version = models.Version.objects.create(publish_date=publish_date)
        blocks = self.load_geodata(version)
        columns, records = self.analyze(blocks)
        self.save_data(version, columns, records)

        # The new version can be activated now that all data is loaded.
        version.activate()

    def get_last_publication_date(self):
        """Return the publication date for the most recent downloaded data."""
        # Find the direct subdirectories of the GEODATA_DIR.
        geodata_dirs = next(os.walk(settings.GEODATA_DIR))[1]

        # As a basic sanity check, ignore directories in the GEODATA_DIR
        # that don't match our expectation of what was downloaded.
        unexpected = [d for d in geodata_dirs if not self.GEODATA_REGEX.match(d)]
        if unexpected:
            logger.warning(
                "Ignoring unexpected directories in GEODATA_DIR: "
                "{}".format(unexpected))
            geodata_dirs = [d for d in geodata_dirs if d not in unexpected]

        # This command should be run after downloading the data.
        if not geodata_dirs:
            raise CommandError(
                "No Geodata has been downloaded. Make sure to run "
                "`python manage.py download_geodata` before running this command.")

        # Geodata directories follow the format GeoLite2-City-CSV_YYYYMMDD.
        # Therefore, the most recent directory will be last when sorted.
        most_recent = sorted(geodata_dirs)[-1]

        # Coerce a date from the most recent directory name,
        #   e.g., GeoLite2-City-CSV_20160802 -> datetime.date(2016, 8, 2)
        publish_date = self.GEODATA_REGEX.match(most_recent).groupdict()
        publish_date = datetime.date(**{k: int(v) for k, v in publish_date.items()})

        return publish_date

    def load_geodata(self, version):
        """Load the most recently downloaded geodata as DataFrames."""
        blocks_filename = os.path.join(
            settings.GEODATA_DIR,
            "GeoLite2-City-CSV_{}/".format(version.publish_date.strftime('%Y%m%d')),
            "GeoLite2-City-Blocks-IPv6.csv")
        logger.info("Loading blocks data from {}".format(blocks_filename))

        try:
            blocks = pd.read_csv(blocks_filename)
        except FileNotFoundError as e:
            error_msg = (
                "Error loading geodata from file. "
                "From error: {}".format(str(e)))
            raise CommandError(error_msg) from e

        return blocks

    def analyze(self, blocks):
        """Analyze data to determine IPV6 density per geographic location."""
        logger.info("Analyzing blocks and locations data.")

        # Basic sanity check that the data uses the columns we depend on.
        block_columns = ('network', 'latitude', 'longitude')
        if not all(c in blocks.columns for c in block_columns):
            raise CommandError(
                "Block data expected to have at least these columns: {}\n"
                "Instead, found these columns: {}".format(
                    block_columns, blocks.columns))

        # Calculate the density of IP addresses at each geographical point.
        # The density of a network range is the number of IP addresses it covers.
        # NOTE: This is fairly slow (~75 sec) on 3 million rows.
        blocks['density'] = blocks['network'].apply(
            lambda n: ipaddress.IPv6Network(n).num_addresses)

        # Remove columns that we aren't interested in.
        result = blocks[['latitude', 'longitude', 'density']]

        # Each location may have more than one range of addresses.
        # The final result should be the sum of densities at a point.
        result = result.groupby(['latitude', 'longitude']).sum().reset_index()

        return list(result.columns), result.to_records(index=False)

    def save_data(self, version, columns, records):
        """Persist records to the database for a given Version."""
        logger.info("Persisting records for {}...".format(version))
        locations = []
        for record in records:
            # Associate each record item with the column it represents.
            fields = dict(zip(columns, record))

            locations.append(models.Location(version=version, **fields))
        models.Location.objects.bulk_create(locations)
        logger.info("Saved {} records for {}.".format(len(locations), version))
