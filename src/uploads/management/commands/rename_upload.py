import csv
import os.path
import re
import shutil
from hitchcock import settings

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
# from django.db.models import Model

from uploads.models import Video, Audio, Text, VttTrack


class Command(BaseCommand):
    help = 'Change the filename associated with an upload'

    def add_arguments(self, parser):
        parser.add_argument('type_of_upload', choices=['Video', 'Audio', 'Text', 'VttTrack'])
        parser.add_argument('current_name', nargs=1, type=str)
        parser.add_argument('new_name', nargs=1, type=str)

    def handle(self, *args, **options):
        type_of_upload = eval(options['type_of_upload'])
        current_name = options['current_name'][0]
        new_name = options['new_name'][0]

        matching_uploads = type_of_upload.objects.filter(upload__contains=current_name)
        print(matching_uploads)
        for u in matching_uploads:
            if os.path.split(u.upload.name)[1] == current_name:
                print(u.upload.name)
                with open(os.path.join(settings.MEDIA_ROOT, u.upload.name), 'rb') as f:
                    u.upload.save(new_name, File(f))
