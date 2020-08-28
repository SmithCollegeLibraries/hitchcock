from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'opensesame'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost",]
BASE_URL = "http://localhost:8000"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Backups
# https://django-dbbackup.readthedocs.io/en/master/installation.html
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/vagrant/test_db_backups/'}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
MEDIA_ROOT = '/vagrant/test-media-dir/'
AV_SUBDIR_NAME = 'av/'
AUDIO_ALBUMS_SUBDIR_NAME = 'av/audio-albums/'
TEXT_SUBDIR_NAME = 'text/'
# VTT files are saved in a subdir under TEXT_SUBDIR_NAME
VTT_SUBDIR_NAME = 'vtt/'
# _definst_/ required for streams in subdirectories
WOWZA_ENDPOINT = 'http://localhost:1935/hitchcock/_definst_/'
TEXTS_ENDPOINT = 'http://localhost:9999/'


## PANOPTO SETTINGS
PANOPTO_SERVER = 'smith.hosted.panopto.com'
PANOPTO_FOLDER_ID = '9bbc13a3-2be9-4055-b416-ac1c00e11240'
PANOPTO_CLIENT_ID = 'cfc6b19d-ace8-4f26-ba48-ac1c01243e6f'
PANOPTO_CLIENT_SECRET = 'AtGQjDH9NBOnEfHmBlzNik3ftoA6ly0el8Un47+8wPk='
PANOPTO_UPLOAD_MANIFEST_TEMPLATES = '/vagrant/hitchcock/src/uploads/panopto/xml_templates/'
PANOPTO_AUTH_CACHE_FILE_PATH = '/vagrant/'
