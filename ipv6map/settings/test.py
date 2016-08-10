import logging

from .base import *  # noqa


CELERY_ALWAYS_EAGER = True

COMPRESS_ENABLED = False

# Quiet logging.
logging.disable(logging.CRITICAL)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

SECRET_KEY = 'secret-key' * 5
