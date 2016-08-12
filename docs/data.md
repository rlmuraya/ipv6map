# Retrieving and syncing data

The data for this project must be regularly downloaded and synced on each
system that it runs on.

## Downloading data

To download the latest IPv6 address data, run this management command::

    python manage.py download_geodata

This retrieves the latest data from the Geodata source, and saves it in
the directory defined in ``settings.GEODATA_DIR``. This directory is included
in the ``.gitignore`` file to avoid publishing large files.

The management command downloads each publication version of the data to a
separate subdirectory. If the publication version has already been downloaded,
it will be overwritten by this command.

The ``sync_geodata`` management command should always be run after this
command completes successfully.


## Syncing data

To sync the database with the latest downloaded IPv6 data, run this management
command::

    python manage.py sync_geodata

This command should be run after the ``download_geodata`` command. By default,
it will not attempt to sync data if the most recent version of the data is
already in the database. To force the creation of new data, use the
``--force-create`` flag.

## Scheduling updates

For each system this project runs on, these commands should be run in tandem
(first ``download_geodata``, then ``sync_geodata``) once to bootstrap data for
the system, then regularly (such as via Celery or cron) to match the
publication schedule of the data source. At time of writing, GeoLite2
publishes updated IPv6 data monthly on the first Tuesday.
