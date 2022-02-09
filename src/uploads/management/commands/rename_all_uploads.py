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
from uploads.models import get_upload_path


class Command(BaseCommand):
    help = ("Change the filename associated with all uploads of a given type, "
            "based on the upload's title")

    def add_arguments(self, parser):
        parser.add_argument('type_of_upload', choices=['Video', 'Audio', 'Text', 'VttTrack'])

    def handle(self, *args, **options):
        type_of_upload = eval(options['type_of_upload'])

        all_uploads_of_type = type_of_upload.objects.all()
        # print(matching_uploads)
        for u in all_uploads_of_type:
            print(u.upload.name)
            u.rename_upload(get_upload_path(u, u.upload.name))
