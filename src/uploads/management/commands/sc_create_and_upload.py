import csv
import cv2
import os.path

from datetime import datetime
from hitchcock import settings
from math import floor, ceil

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from uploads.models import Folder, Video, VideoPlaylist, VideoPlaylistLink, Audio, AudioPlaylist, AudioPlaylistLink
from uploads.management.commands.create_uploads_from_csv import get_location_of_file, add_upload_to_database, is_audio, is_video
from uploads.panopto.panopto_oauth2 import RefreshAccessTokenFailed


class UploadSkipped(Exception):
    pass


def add_audio_to_playlist(upload_object, playlist_title, playlist_order):
    playlist_to_add_to = AudioPlaylist.objects.get(title=playlist_title)
    new_playlist_link = AudioPlaylistLink(
        av=upload_object,
        playlist=playlist_to_add_to,
        playlist_order=playlist_order,
    )
    new_playlist_link.save()

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
        minutes = floor(time_in_s // 60)
        seconds = time_in_s - (60 * minutes)
        return f'{minutes}:{ceil(seconds):02}'
    except TypeError:
        return '0:00'


class Command(BaseCommand):
    help = '''Add the uploads in the spreadsheet given to the database.
Columns:
   0 - Filepath
   1 - Title
   2 - Description (should include ArchivesSpace link)
   3 - Visibility (Open access, Smith only, Private)
   4 - Playlist_name
   5 - Playlist_order
   5 - Hitchcock_video_ID or Hitchcock_audio_ID (will be provided)
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

        audio_playlists_to_save = []
        video_playlists_to_save = []

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
                panopto_session_id = row[6]
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

                    if is_video(file_name):
                        # Capture video duration
                        # https://stackoverflow.com/a/61572332/2569052
                        cap = cv2.VideoCapture(file_location)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        video_duration_in_s = frame_count / fps if fps else 0
                    else:
                        video_duration_in_s = 0
                    video_duration = seconds_to_minutes_seconds(video_duration_in_s)

                    try:
                        added_upload = add_upload_to_database(
                            title=title,
                            # specifying the name is needed so that the file
                            # goes in the media folder, rather than attempting
                            # to make a copy in the import folder
                            upload=File(existing_file, name=file_name),
                            notes='',
                            description=description,
                            folder=folder,
                            panopto_session_id=panopto_session_id,
                        )
                        if not added_upload:
                            raise UploadSkipped
                        # Add to playlist as well
                        if playlist_name and playlist_order:
                            if is_audio(file_name):
                                # Create new playlist if it doesn't exist already
                                if not AudioPlaylist.objects.filter(title=playlist_name).exists():
                                    new_playlist = AudioPlaylist(
                                        title=playlist_name,
                                        folder=folder,
                                    )
                                    new_playlist.save()
                                add_audio_to_playlist(added_upload, playlist_name, playlist_order)
                                # Keep track of playlists to save, so that
                                # they can all just be saved at the end
                                if playlist_name not in audio_playlists_to_save:
                                    audio_playlists_to_save.append(playlist_name)

                            elif is_video(file_name):
                                # Create new playlist if it doesn't exist already
                                if not VideoPlaylist.objects.filter(title=playlist_name).exists():
                                    new_playlist = VideoPlaylist(
                                        title=playlist_name,
                                        folder=folder,
                                    )
                                    new_playlist.save()
                                add_video_to_playlist(added_upload, playlist_name, playlist_order)
                                # Keep track of playlists to save, so that
                                # they can all just be saved at the end
                                if playlist_name not in video_playlists_to_save:
                                    video_playlists_to_save.append(playlist_name)

                    except UploadSkipped:
                        log_writer.writerow([
                            *row[0:6],
                            'SKIPPED',
                            'SKIPPED',
                            video_duration,
                        ])
                    except RefreshAccessTokenFailed:
                        log_writer.writerow([
                            *row[0:6],
                            'ERROR',
                            'ERROR',
                            video_duration,
                        ])
                        print(f"You need to set up the refresh token. Go to {settings.BASE_URL}/renew-panopto-token to set it up. More details in README.md.")
                        print(f"You can delete {title} from Hitchcock and upload it again.")
                        break
                    else:
                    # If the upload was successful, after logging, delete
                    # the file.
                        log_writer.writerow([
                            *row[0:6],
                            added_upload.id,
                            f'{settings.BASE_URL}/videos/{str(added_upload.id)}',
                            video_duration,
                        ])
                        os.remove(file_location)

        # Now save all the playlists
        for playlist_name in audio_playlists_to_save:
            # If it's an audio
            audio_playlist_object = AudioPlaylist.objects.filter(title=playlist_name).first()
            if audio_playlist_object:
                audio_playlist_object.save()
        for playlist_name in video_playlists_to_save:
            # If it's a video
            video_playlist_object = VideoPlaylist.objects.filter(title=playlist_name).first()
            if video_playlist_object:
                video_playlist_object.save()
