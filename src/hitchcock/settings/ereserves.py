from .base import *

# List of people who get 500 error notifications:
# https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-ADMINS
ADMINS = [
    ('Tristan Chambers', 'tchambers@smith.edu'),
]

# SECURITY WARNING: keep the secret key used in production secret!
with open('/mnt/nfs/reserves/app/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['ereserves.smith.edu',]
BASE_URL = "http://ereserves.smith.edu/hitchcock"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/mnt/nfs/reserves/app/database.cnf',
        },
    }
}

# Backups
# https://django-dbbackup.readthedocs.io/en/master/installation.html
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/mnt/nfs/reserves/data_backups'}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/hitchcock/static/'
STATIC_ROOT = '/mnt/nfs/reserves/app/static'
MEDIA_ROOT = '/mnt/nfs/reserves/'
AV_SUBDIR_NAME = 'av/'
AUDIO_ALBUMS_SUBDIR_NAME = 'av/audio-albums/'
TEXT_SUBDIR_NAME = 'text/'
# VTT files are saved in a subdir under TEXT_SUBDIR_NAME
VTT_SUBDIR_NAME = 'vtt/'
# NOTE: _definst_/ required subdirectories to work in Wowza
WOWZA_ENDPOINT = 'http://ereserves.smith.edu:1935/reserves/_definst_/'
TEXTS_ENDPOINT = 'https://ereserves.smith.edu/reserves/text/'

# Set csrf and session cookies to "secure" to prevent the browser from
# ever sending them over HTTPs.
# https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/#https
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# logging
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'handlers': {
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/hitchcock-debug.log',
#        },
#    },
#    'loggers': {
#        'django': {
#            'handlers': ['file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#    },
#}
