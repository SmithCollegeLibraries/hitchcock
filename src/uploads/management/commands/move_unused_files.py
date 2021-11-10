import csv
import os.path
import re
import shutil
from hitchcock import settings

from django.core.files import File
from django.core.management.base import BaseCommand

from uploads.models import Text, Audio, Video, VttTrack


UNUSED = 'unused'
MODELS_TO_PROCESS = [Text, Audio, Video, VttTrack]
DIRECTORIES_TO_PROCESS = [
    'av/video',
    'text/articles',
]
EXTENSIONS = ['.mp3', '.mp4', '.mpeg3', '.mpeg4', '.wav', '.vtt', '.pdf']


class Command(BaseCommand):
    help = 'Move unused files to a separate directory for deletion'

    def add_arguments(self, parser):
        parser.add_argument('unused_directory', nargs="?", type=str)

    def handle(self, *args, **options):
        if options['unused_directory']:
            unused_directory = options['unused_directory'][0]
        else:
            unused_directory = UNUSED

        # First make sure the 'unused' folder is present
        if not os.path.isdir(os.path.join(settings.MEDIA_ROOT, UNUSED)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, UNUSED))

        # Go through the audio, video, vtt, and text files and get
        # the file location of every file being used
        files_in_use = []
        for model in MODELS_TO_PROCESS:
            for instance in model.objects.all():
                files_in_use.append(instance.upload.path)

        # Now go through the media directories and get the file location
        # of every file, used or not (for files with one of the extensions
        # listed; we won't want to move other kinds of files)
        all_media_files = []
        for d in DIRECTORIES_TO_PROCESS:
            # Get full path of each directory listed at the top of this
            # document -- splitting at the slash first
            p = os.path.join(settings.MEDIA_ROOT, *d.split('/'))
            # For each file in each of those directories, add it to the list
            for f in os.listdir(p):
                extension = os.path.splitext(f)[1]
                if extension in EXTENSIONS:
                    all_media_files.append(os.path.join(p, f))

        for f in all_media_files:
            if f not in files_in_use:
                shutil.move(f, os.path.join(settings.MEDIA_ROOT, UNUSED))
