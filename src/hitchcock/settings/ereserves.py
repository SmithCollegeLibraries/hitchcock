from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'opensesame'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/hitchcock-debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
