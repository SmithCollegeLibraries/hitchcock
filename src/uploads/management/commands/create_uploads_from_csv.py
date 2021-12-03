import csv
import os.path
import re
import shutil
from datetime import datetime
from hitchcock import settings

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from uploads.models import Video

LOGFILE = 'log.txt'

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

def add_video_to_database(title, notes, upload, panopto_session_id):
    try:
        new_video = Video(
            title=title,
            notes=notes,
            upload=upload,
            panopto_session_id=panopto_session_id,
            lock_panopto_session_id=True,
        )
        new_video.save()
        return True
    except IntegrityError:
        print(f"Cannot add a video with duplicate title {title}.")
        new_title = input("Please enter new title, or ENTER to skip: ")
        print(new_title)
        if not new_title:
            return False
        else:
            return add_video_to_database(new_title, notes, upload, panopto_session_id)


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
        # First make sure the log file is present
        # https://stackoverflow.com/a/43081892/2569052
        log_path = os.path.join(import_directory, LOGFILE)
        try:
            logfile = open(log_path, 'x')
            logfile.write('Import log\n')
            logfile.close()
        except FileExistsError:
            pass
        # Now open the spreadsheet and start processing the items in it
        with open(spreadsheet_file) as f, open(log_path, 'a') as logfile:
            # Log the date and time of this run
            logfile.write('\n' + datetime.now().strftime('%Y-%m-%d %H:%M:%S%z') + '\n')
            rows = csv.reader(f)
            for row in rows:
                print(row)
                title = row[2]
                notes = row[3]
                upload_url = row[4]
                file_location = get_location_of_file(import_directory, row[5])

                # Don't process items already in Hitchcock
                if 'hitchcock' in upload_url:
                    continue
                if not file_location:
                    continue
                # Separate the (dir, name) tuple that makes up file_location
                with open(file_location, 'rb') as existing_file:
                    # Split off the filename proper from the path
                    file_name = os.path.split(file_location)[1]
                    # Results of video add saved in "skipped"
                    success = add_video_to_database(
                        title=title,
                        notes=notes,
                        # specifying the name is needed so that the file
                        # goes in the media folder, rather than attempting
                        # to make a copy in the import folder
                        upload=File(existing_file, name=file_name),
                        panopto_session_id=get_panopto_session_id(upload_url),
                    )
                    if success:
                        # Log the filename added to Hitchcock and delete file
                        # from import location
                        logfile.write(file_location + '\n')
                        os.remove(file_location)
                    else:
                        logfile.write('ERROR: ' + file_location + '\n')
