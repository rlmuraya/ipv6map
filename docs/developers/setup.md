# Local Development

Use this guide to bootstrap your local development environment.

**NOTE:** These instructions are written with Ubuntu in mind. Some adjustments
may be needed for Mac setup.

1. Ensure that you have the following installed on your system:

    * Python 3.5
    * Postgres
    * pip
    * virtualenv
    * virtualenvwrapper
    * git

2. Clone the repo:

        git clone git@github.com:rlmuraya/ipv6map.git
        cd ipv6map/

3. Create a virtualenv using Python 3.5 and install the requirements:

        mkvirtualenv ipv6map --python=/usr/bin/python3.5
        workon ipv6map
        pip install -r requirements/local.txt

4. Create a local settings file from the example template:

        cp ipv6map/settings/local.py.example ipv6map/settings/local.py

   You may edit this file to make environment changes that are local to your
   machine. This file is listed in the ``.gitignore`` file and should never
   be checked into GitHub.

5. Add the project directory to the Python path in your virtual environment::

        add2virtualenv .

6. Configure the default project settings file within your virtual environment,
   and restart the environment so that the change will take effect:

        echo "export DJANGO_SETTINGS_MODULE=ipv6map.settings.local" >> $VIRTUAL_ENV/bin/postactivate
        echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate
        deactivate
        workon ipv6map

7. Create a Postgres database::

        createdb -E UTF-8 ipv6map

   If required, you should update your local settings to reflect your database
   name, username, and password.

8. Run database migrations:

        python manage.py migrate

   If desired, you may create a superuser account now:

        python manage.py createsuperuser

9. See the docs for [syncing data](data.md) to get the latest IPv6 data from
   GeoLite2.

10. Run the development server and navigate to [localhost:8000](http://localhost:8000):

        python manage.py runserver
