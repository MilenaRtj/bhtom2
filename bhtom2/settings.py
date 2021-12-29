"""
Django settings for your TOM project.

Originally generated by 'django-admin startproject' using Django 2.1.1.
Generated by ./manage.py tom_setup on July 15, 2021, 7:27 p.m.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import logging.config
import os
import sys
import tempfile

from dotenv import dotenv_values

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from bhtom2.external_service.data_source_information import DataSource, TARGET_NAME_KEYS


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Environment variables
secret = dotenv_values(os.path.join(BASE_DIR, 'bhtom2/.bhtom.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jkg5zb*xutcc+93y!00$7z409yrh%6#i@f)+h!$lyr3vqo9c)e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [] + list(secret.get("ALLOWED_HOSTS", 'localhost').split(','))
SITE_ID = int(secret.get("SITE_ID", 1))

CPCS_BASE_URL = secret.get('CPCS_BASE_URL', None)
CPCS_DATA_ACCESS_HASHTAG = secret.get('CPCS_DATA_ACCESS_HASHTAG', None)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'guardian',
    'tom_common',
    'django_comments',
    'bootstrap4',
    'crispy_forms',
    'rest_framework',
    'django_filters',
    'django_gravatar',
    'tom_targets',
    'tom_alerts',
    'tom_catalogs',
    'tom_observations',
    'tom_dataproducts',
    'tom_registration',
    'rest_framework.authtoken',
    'bhtom2.apps.BHTOM2Config'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tom_common.middleware.Raise403Middleware',
    'tom_common.middleware.ExternalServiceMiddleware',
    'tom_common.middleware.AuthStrategyMiddleware',
    'tom_registration.middleware.RedirectAuthenticatedUsersFromRegisterMiddleware',
]

ROOT_URLCONF = 'bhtom2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'bhtom2/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

WSGI_APPLICATION = 'bhtom2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': secret.get("POSTGRES_DB_NAME", 'bhtom2'),
        'ENGINE': 'django.db.backends.postgresql',
        'USER': secret.get("POSTGRES_DB_USER", 'bhtom'),
        'PASSWORD': secret.get("POSTGRES_PASSWORD", ""),
        'HOST': secret.get('POSTGRES_HOST', 'localhost'),
        'PORT': secret.get('POSTGRES_PORT', 5432),
        'TEST': {
            'NAME': secret.get("POSTGRES_TEST_DB_NAME", 'test_bhtom2')
        }
    },
}

# Test Database
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3' # Django uses an in-memory database if sqlite3
    DATABASES['default']['PASSWORD'] = secret.get("POSTGRES_TEST_PASSWORD", "")
    DATABASES['default']['HOST'] = secret.get("POSTGRES_TEST_HOST", "localhost")
    DATABASES['default']['PORT'] = secret.get("POSTGRES_TEST_PORT", 5432)


MIGRATION_MODULES = {
    'bhtom2': 'bhtom2.migrations'
}


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

TOM_REGISTRATION = {
    'REGISTRATION_AUTHENTICATION_BACKEND': 'django.contrib.auth.backends.AllowAllUsersModelBackend',
    'REGISTRATION_REDIRECT_PATTERN': 'home',
    'SEND_APPROVAL_EMAILS': True
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATETIME_FORMAT = 'Y-m-d H:m:s'
DATE_FORMAT = 'Y-m-d'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '_static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'bhtom2/static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'data')
MEDIA_URL = '/data/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'graypy': {
            'level': 'INFO',
            'class': 'graypy.GELFTCPHandler',
            'host': secret.get('GRAYLOG_HOST', 'localhost'),
            'port': secret.get('GRAYLOG_PORT', 12201),
        },
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['graypy', 'console'],
            'level': 'INFO'
        }
    },
}

# Caching
# https://docs.djangoproject.com/en/dev/topics/cache/#filesystem-caching

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': tempfile.gettempdir()
    }
}

# TOM Specific configuration
TARGET_TYPE = 'SIDEREAL'

FACILITIES = {
    'LCO': {
        'portal_url': 'https://observe.lco.global',
        'api_key': '',
    },
    'GEM': {
        'portal_url': {
            'GS': 'https://139.229.34.15:8443',
            'GN': 'https://128.171.88.221:8443',
        },
        'api_key': {
            'GS': '',
            'GN': '',
        },
        'user_email': '',
        'programs': {
            'GS-YYYYS-T-NNN': {
                'MM': 'Std: Some descriptive text',
                'NN': 'Rap: Some descriptive text'
            },
            'GN-YYYYS-T-NNN': {
                'QQ': 'Std: Some descriptive text',
                'PP': 'Rap: Some descriptive text',
            },
        },
    },
}

# Define the valid data product types for your TOM. Be careful when removing items, as previously valid types will no
# longer be valid, and may cause issues unless the offending records are modified.
DATA_PRODUCT_TYPES = {
    'photometry': ('photometry', 'Photometry'),
    'fits_file': ('fits_file', 'FITS File'),
    'spectroscopy': ('spectroscopy', 'Spectroscopy'),
    'image_file': ('image_file', 'Image File')
}

DATA_PROCESSORS = {
    'photometry': 'tom_dataproducts.processors.photometry_processor.PhotometryProcessor',
    'spectroscopy': 'tom_dataproducts.processors.spectroscopy_processor.SpectroscopyProcessor',
}

TOM_FACILITY_CLASSES = [
    'tom_observations.facilities.lco.LCOFacility',
    'tom_observations.facilities.gemini.GEMFacility',
    'tom_observations.facilities.soar.SOARFacility',
    'tom_observations.facilities.lt.LTFacility'
]

# TODO: investigate why are they missing

TOM_ALERT_CLASSES = [
    'bhtom2.brokers.gaia_alerts.GaiaAlertsBroker',
    'bhtom2.brokers.aavso.AAVSOBroker',
    'bhtom2.brokers.ztf.ZTFBroker',
    'tom_alerts.brokers.alerce.ALeRCEBroker',
    'tom_alerts.brokers.antares.ANTARESBroker',
    'tom_alerts.brokers.lasair.LasairBroker',
    'tom_alerts.brokers.mars.MARSBroker',
    'tom_alerts.brokers.scimma.SCIMMABroker',
    'tom_alerts.brokers.scout.ScoutBroker',
    'tom_alerts.brokers.tns.TNSBroker',
    'tom_alerts.brokers.fink.FinkBroker',
]

BROKERS = {
    'TNS': {
        'api_key': ''
    }
}

TOM_HARVESTER_CLASSES = [
    'bhtom2.harvesters.gaia_alerts.GaiaAlertsHarvester',
    'bhtom2.harvesters.tns.TNSHarvester',
    'tom_catalogs.harvesters.simbad.SimbadHarvester',
    'tom_catalogs.harvesters.ned.NEDHarvester',
    'tom_catalogs.harvesters.jplhorizons.JPLHorizonsHarvester',
]

HARVESTERS = {
    'TNS': {
        'api_key': ''
    }
}

# Define extra target fields here. Types can be any of "number", "string", "boolean" or "datetime"
# See https://tomtoolkit.github.io/docs/target_fields for documentation on this feature
# For example:
# EXTRA_FIELDS = [
#     {'name': 'redshift', 'type': 'number'},
#     {'name': 'discoverer', 'type': 'string'}
#     {'name': 'eligible', 'type': 'boolean'},
#     {'name': 'dicovery_date', 'type': 'datetime'}
# ]
EXTRA_FIELDS = [
    {'name': TARGET_NAME_KEYS[DataSource.Gaia], 'type': 'string'},
    {'name': TARGET_NAME_KEYS[DataSource.CPCS], 'type': 'string'},
    {'name': TARGET_NAME_KEYS[DataSource.ZTF], 'type': 'string'},
    {'name': TARGET_NAME_KEYS[DataSource.AAVSO], 'type': 'string'},
    {'name': TARGET_NAME_KEYS[DataSource.GAIA_DR2], 'type': 'string'},
    {'name': TARGET_NAME_KEYS[DataSource.TNS], 'type': 'string'},
    {'name': 'classification', 'type': 'string'},
    {'name': 'tweet', 'type': 'boolean'},
    {'name': 'last_jd', 'type': 'number'},
    {'name': 'last_mag', 'type': 'number'},
    {'name': 'priority', 'type': 'number'},
    {'name': 'dicovery_date', 'type': 'datetime'},
    {'name': 'cadence', 'type': 'number'},
    {'name': 'sun_separation', 'type': 'number'},
    {'name': 'dont_update_me', 'type': 'boolean', 'hidden': True}]

# Authentication strategy can either be LOCKED (required login for all views)
# or READ_ONLY (read only access to views)
AUTH_STRATEGY = 'READ_ONLY'

# Row-level data permissions restrict users from viewing certain objects unless they are a member of the group to which
# the object belongs. Setting this value to True will allow all `ObservationRecord`, `DataProduct`, and `ReducedDatum`
# objects to be seen by everyone. Setting it to False will allow users to specify which groups can access
# `ObservationRecord`, `DataProduct`, and `ReducedDatum` objects.
TARGET_PERMISSIONS_ONLY = True

# URLs that should be allowed access even with AUTH_STRATEGY = LOCKED
# for example: OPEN_URLS = ['/', '/about']
OPEN_URLS = []

HOOKS = {
    'target_post_save': 'bhtom2.hooks.target_post_save',
    'observation_change_state': 'tom_common.hooks.observation_change_state',
    'data_product_post_upload': 'tom_dataproducts.hooks.data_product_post_upload',
    'data_product_post_save': 'tom_dataproducts.hooks.data_product_post_save',
    'multiple_data_products_post_save': 'tom_dataproducts.hooks.multiple_data_products_post_save',
}

AUTO_THUMBNAILS = False

THUMBNAIL_MAX_SIZE = (0, 0)

THUMBNAIL_DEFAULT_SIZE = (200, 200)

HINTS_ENABLED = False
HINT_LEVEL = 20

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

try:
    from local_settings import * # noqa
except ImportError:
    pass

sentry_sdk.init(
    dsn=secret.get('SENTRY_SDK_DSN', ''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

GAIA_ALERTS_PATH: str = 'http://gsaweb.ast.cam.ac.uk'
AAVSO_API_PATH: str = 'https://www.aavso.org/vsx/index.php'