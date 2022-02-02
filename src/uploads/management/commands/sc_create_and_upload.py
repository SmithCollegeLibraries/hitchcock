import csv
import os.path
import re
import shutil

from datetime import datetime
from ffprobe import FFProbe
from hitchcock import settings
from math import ceil

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from uploads.models import Folder, Video, VideoPlaylist, VideoPlaylistLink
from uploads.management.commands.create_uploads_from_csv import get_location_of_file, add_video_to_database


def add_video_to_playlist(upload_object, playlist_title, playlist_order):
    playlist_to_add_to = VideoPlaylist.objects.get(title=playlist_title)
    new_playlist_link = VideoPlaylistLink(
        av=upload_object,
        playlist=playlist_to_add_to,
        playlist_order=playlist_order,
    )
    new_playlist_link.save()

def seconds_to_minutes_seconds(time_in_s):
    try:
        minutes = time_in_s // 60
        seconds = time_in_s - (60 * minutes)
        return f'{minutes}:{ceil(seconds)}'
    except TypeError:
        return '0:00'


class Command(BaseCommand):
    help = '''Add the videos in the spreadsheet given to the database.
Columns:
   0 - Filepath
   1 - Title
   2 - Description (should include ArchivesSpace link)
   3 - Visibility (Open access, Smith only, Private)
   4 - Playlist_name
   5 - Playlist_order
   5 - Hitchcock_video_ID (will be provided)
   6 - Hitchcock_URL (will be provided)
   7 - Video duration (will be provided)
'''

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_location', nargs=1, type=str)
        parser.add_argument('import_directory', nargs=1, type=str)

    def handle(self, *args, **options):
        spreadsheet_path = options['spreadsheet_location'][0]
        import_directory = options['import_directory'][0]

        # Create log CSV based on existing CSV name, plus a timestamp.
        log_path = (os.path.splitext(spreadsheet_path)[0] +
                    f'--{datetime.now():%Y-%m-%d--%H-%M}' +
                    '.csv')
        # Now open the spreadsheet and start processing the items in it
        with open(spreadsheet_path) as f, open(log_path, 'w') as logfile:
            logfile.write(f.readline())  # Copy header information to log
            rows = csv.reader(f)
            log_writer = csv.writer(logfile)
            for row in rows:
                print('\t'.join(row))
                file_location = get_location_of_file(import_directory, row[0])
                title = row[1]
                description = row[2]
                folder_name = row[3]
                playlist_name = row[4]
                playlist_order = row[5]
                try:
                    folder = Folder.objects.get(name=folder_name)
                except:
                    folder = Folder.objects.get(id=1)
                    print('Warning: incorrect folder name provided; using default folder')

                if not file_location:
                    continue
                # Separate the (dir, name) tuple that makes up file_location
                with open(file_location, 'rb') as existing_file:
                    # Split off the filename proper from the path
                    file_name = os.path.split(file_location)[1]

                    # Capture video duration
                    # https://stackoverflow.com/a/61572332/2569052
                    metadata = FFProbe(file_location)
                    video_duration_in_s = 0
                    for stream in metadata.streams:
                        if stream.is_video():
                            video_duration_in_s = max(video_duration_in_s, float(stream.duration))
                    video_duration = seconds_to_minutes_seconds(video_duration_in_s)

                    # Results of video add saved in "skipped"
                    added_video = add_video_to_database(
                        title=title,
                        # specifying the name is needed so that the file
                        # goes in the media folder, rather than attempting
                        # to make a copy in the import folder
                        upload=File(existing_file, name=file_name),
                        notes='',
                        description=description,
                        folder=folder,
                    )
                    # Log the filename added to Hitchcock and delete file
                    # from import location
                    if added_video:
                        log_writer.writerow([
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                            row[5],
                            added_video.id,
                            f'{settings.BASE_URL}/{str(added_video.id)}',
                            video_duration,
                        ])
                        os.remove(file_location)
                        # Add to playlist as well
                        if playlist_name and playlist_order:
                            if VideoPlaylist.objects.filter(title=playlist_name).exists():
                                add_video_to_playlist(added_video, playlist_name, playlist_order)
                            else:
                                print(f"Can't add to playlist {playlist_name} (doesn't exist)")
                    else:
                        log_writer.writerow([
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                            row[5],
                            'ERROR',
                            '',
                            '',
                        ])
