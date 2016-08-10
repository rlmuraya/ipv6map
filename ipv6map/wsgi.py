import os

from django.core.wsgi import get_wsgi_application

from . import load_env


load_env.load_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipv6map.settings.local")

application = get_wsgi_application()
