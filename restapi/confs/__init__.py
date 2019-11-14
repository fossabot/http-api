# -*- coding: utf-8 -*-

import os
import re
from urllib.parse import urlparse

AVOID_COLORS_ENV_LABEL = 'TESTING_FLASK'
STACKTRACE = False
REMOVE_DATA_AT_INIT_TIME = False

#################
# ENDPOINTS bases
API_URL = '/api'
AUTH_URL = '/auth'
STATIC_URL = '/static'
BASE_URLS = [API_URL, AUTH_URL]

#################
# THE APP
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '8080'
USER_HOME = os.environ['HOME']
UPLOAD_FOLDER = os.environ.get('UPLOAD_PATH', '/uploads')
SECRET_KEY_FILE = os.environ.get('JWT_APP_SECRETS') + "/secret.key"

#################
PRODUCTION = False
# DEBUG = False
if os.environ.get('APP_MODE', '') == 'production':
    PRODUCTION = True
# elif os.environ.get('APP_MODE', '') == 'debug':
#     DEBUG = True

#################
# SQLALCHEMY
BASE_DB_DIR = '/dbs'
SQLLITE_EXTENSION = 'db'
SQLLITE_DBFILE = 'backend' + '.' + SQLLITE_EXTENSION
dbfile = os.path.join(BASE_DB_DIR, SQLLITE_DBFILE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile

SENTRY_URL = os.environ.get('SENTRY_URL')
if SENTRY_URL is not None and SENTRY_URL.strip() == '':
    SENTRY_URL = None


def get_api_url(request_object, production=False):
    """ Get api URL and PORT

    Usefull to handle https and similar
    unfiltering what is changed from nginx and container network configuration

    Warning: it works only if called inside a Flask endpoint
    """

    api_url = request_object.url_root

    if production:
        parsed = urlparse(api_url)
        if parsed.port is not None and parsed.port == 443:
            removed_port = re.sub(r':[\d]+$', '', parsed.netloc)
            api_url = parsed._replace(scheme="https", netloc=removed_port).geturl()

    return api_url
