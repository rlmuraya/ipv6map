import os

from .base import *  # noqa


DOMAIN = os.environ.get('DOMAIN')

ALLOWED_HOSTS = ['.{}'.format(DOMAIN)]

SECRET_KEY = os.environ.get('SECRET_KEY', None)
