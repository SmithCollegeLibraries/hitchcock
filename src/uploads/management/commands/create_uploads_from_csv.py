import csv
import os.path
import re
import shutil
from hitchcock import settings

from django.core.files import File
from django.core.management.base import BaseCommand

from uploads.models import Video

DONE = 'done'

def get_location_of_file(directory, filename, extension='mp4'):
    '''Returns the actual verified path of the video, or None if
    no such file exists (or it is not found).
    '''
    # Add extension if not provided
    if '.' not in filename:
        filename = filename + '.' + extension
    # Check if the path does exist
    if not os.path.exists(os.path.join(directory, filename)):
        # If a filename is entered, try that; otherwise, skip this one
        print("Searching in", directory, "...")
        print("Couldn't find", filename)
        new_filename = input('Enter the correct filename, or ENTER to skip. ')
        if not new_filename:
            return None
        else:
            # If no extension is provided, add the default
            if '.' not in new_filename:
                new_filename = new_filename + '.' + extension
            return get_location_of_file(directory, new_filename)
    # If the path does exist, return it
    else:
        return os.path.join(directory, filename)

def get_panopto_session_id(url):
    '''Returns just the session ID part of a Panopto session URL.
    Returns None if it is not a valid Panopto session ID.
    '''
    if 'panopto.com' not in url or '?id=' not in url:
        return None
    else:
        return re.match(r'.*\?id=(.*)', url).group(1)


class Command(BaseCommand):
    help = 'Add the videos in the spreadsheet given to the database'

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_file', nargs=1, type=str)
        parser.add_argument('import_directory', nargs=1, type=str)

    # 0 Timestamp
    # 1 Date processed
    # 2 DVD Title
    # 3 Notes
    # 4 Panopto/Hitchcock URL
    # 5 File Name
    # 6 Does the file have subtitles/captions?
    # 7 Backlog: Added to Hitchcock date
    # 8 Backlog: Staff initials
    # 9 Backlog: Hitchcock URL
    # 10 Backlog: Hitchcock URL added to E-Reserves

    def handle(self, *args, **options):
        spreadsheet_file = options['spreadsheet_file'][0]
        import_directory = options['import_directory'][0]
        # First make sure the 'done' folder is present
        if not os.path.isdir(os.path.join(import_directory, DONE)):
            os.mkdir(os.path.join(import_directory, DONE))
        # Now open the spreadsheet and start processing the items in it
        with open(spreadsheet_file) as f:
            rows = csv.reader(f)
            for row in rows:
                # Don't process items already in Hitchcock
                print(row)
                if 'hitchcock' in row[4]:
                    continue
                file_location = get_location_of_file(import_directory, row[5])
                if not file_location:
                    continue
                # Separate the (dir, name) tuple that makes up file_location
                with open(file_location, 'rb') as existing_file:
                    # Split off the filename proper from the path
                    file_name = os.path.split(file_location)[1]
                    new_video = Video(
                        title=row[2],
                        notes=row[3],
                        # specifying the name is needed so that the file
                        # goes in the media folder, rather than attempting
                        # to make a copy in the import folder
                        upload=File(existing_file, name=file_name),
                        panopto_session_id=get_panopto_session_id(row[4]),
                        lock_panopto_session_id=True,
                    )
                    new_video.save()
                shutil.move(file_location, os.path.join(import_directory, DONE))
