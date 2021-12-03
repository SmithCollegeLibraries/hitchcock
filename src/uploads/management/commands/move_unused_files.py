import csv
import os.path
import re
import shutil
from os import walk
from hitchcock import settings

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from uploads.models import Text, Audio, Video, VttTrack


UNUSED = 'unused'
MODELS_TO_PROCESS = [Text, Audio, Video, VttTrack]
EXTENSIONS = ['.mp3', '.mpeg3', '.mpeg4', '.mp4', '.m4a', '.wav', '.vtt', '.pdf']


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
        for (dirpath, dirnames, filenames) in walk(settings.MEDIA_ROOT):
            # For each file in each of those directories, add it to the list
            for n in filenames:
                extension = os.path.splitext(n)[1]
                if extension in EXTENSIONS:
                    all_media_files.append(os.path.join(dirpath, n))

        for f in all_media_files:
            # Don't move if used, or already in the UNUSED folder
            if f not in files_in_use and os.path.join(settings.MEDIA_ROOT, UNUSED) not in f:
                try:
                    shutil.move(f, os.path.join(settings.MEDIA_ROOT, UNUSED))
                # If a file with that name already exists, create a new one
                # with a unique name
                except shutil.Error as err:
                    print(err)
                    filename = os.path.split(f)[1]
                    bare_filename, extension = os.path.splitext(filename)
                    new_filename = bare_filename + '_' + get_random_string(6) + extension
                    shutil.move(f, os.path.join(settings.MEDIA_ROOT, UNUSED, new_filename))
