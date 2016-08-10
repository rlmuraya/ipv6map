import errno
import logging
import os
import re
import tempfile
import zipfile

import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger(__name__)

# Expected location of the block data file in the zipfile from the data source.
BLOCK_DATA_FILE = re.compile(r'^GeoLite2-City-CSV_\d{8}/GeoLite2-City-Blocks-IPv6.csv$')


class Command(BaseCommand):
    help = "Download and prepare data files with IPV6 address locations."

    # Chunk size when streaming data source.
    CHUNK_SIZE = 1024

    # Data describing the locations of IP addresses (by city).
    # For more information, see:
    #   http://dev.maxmind.com/geoip/geoip2/geolite2/
    GEODATA_SOURCE = ("http://geolite.maxmind.com/"
                      "download/geoip/database/GeoLite2-City-CSV.zip")

    def handle(self, *args, **kwargs):
        self.create_geodata_dir()

        # Download the data to a temp file and extract from there.
        # Data will be stored in settings.GEODATA_DIR.
        local_file = tempfile.NamedTemporaryFile('wb')
        try:
            self.download_data(local_file)
            self.unzip_data(local_file)
        finally:
            local_file.close()

    def create_geodata_dir(self):
        """Create the geodata directory if it does not already exist."""
        try:
            os.makedirs(settings.GEODATA_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                error_msg = (
                    "Error creating {} directory. "
                    "From error: {}".format(str(e)))
                raise CommandError(error_msg) from e

    def download_data(self, local_file):
        """Get the zipped geodata file from the original source."""
        try:
            logger.info("Downloading data from {}".format(self.GEODATA_SOURCE))
            response = requests.get(self.GEODATA_SOURCE, stream=True)
            response.raise_for_status()

            # Write response content to the local file.
            logger.info("Saving data locally to temporary file...")
            for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                if chunk:
                    local_file.write(chunk)
            local_file.flush()

            logger.info("Download complete.")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                # Probably a temporary upstream error - try again later.
                error_msg = (
                    "Unable to get geodata from source. Try again later."
                    "From error: {}".format(str(e)))
            else:
                # Probably our error - something may have changed.
                error_msg = (
                    "Unable to get geodata from source. "
                    "Has the download location changed? "
                    "From error: {}".format(str(e)))
            raise CommandError(error_msg) from e

        except requests.exceptions.RequestException as e:
            # Probably a connection problem.
            error_msg = (
                "Unable to get geodata from source. "
                "Is there a connection problem? "
                "From error: {}".format(str(e)))
            raise CommandError(error_msg) from e

    def unzip_data(self, local_file):
        """Unzip downloaded data to a local location."""
        z = zipfile.ZipFile(local_file.name, 'r')

        # Find the location of the Block data file in the zipped file.
        block_file = next((n for n in z.namelist() if BLOCK_DATA_FILE.match(n)), None)
        if not block_file:
            raise CommandError(
                "Could not find block data file in zip contents: "
                "{}".format(z.namelist()))

        logger.info("Unzipping Block data to {}".format(settings.GEODATA_DIR))
        z.extract(block_file, settings.GEODATA_DIR)
