from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'opensesame'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
BASE_URL = "http://localhost:8000"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
MEDIA_ROOT = '/Users/tchambers/code/hitchcock/test-media-dir'
AV_SUBDIR_NAME = 'av/'
AUDIO_ALBUMS_SUBDIR_NAME = 'av/audio-albums/'
TEXT_SUBDIR_NAME = 'text/'
# _definst_/ required for streams in subdirectories
WOWZA_ENDPOINT = 'http://localhost:1935/hitchcock/_definst_/'
TEXTS_ENDPOINT = 'http://localhost:9999/'
