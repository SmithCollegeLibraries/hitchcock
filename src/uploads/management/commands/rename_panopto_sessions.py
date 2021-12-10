import csv
import os.path
import re
import shutil
from os import walk
from hitchcock import settings

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from uploads.models import Audio, Video, create_panopto_requests_session


class Command(BaseCommand):
    help = '''Rename Panopto sessions if they are generated from a
           filename instead of a title.'''

    def add_arguments(self, parser):
        # Parameter to skip confirmation on each rename
        parser.add_argument(
            '--noconfirmation',
            action='store_const',
            const=True,
            help='Use if you do not want to manually confirm each rename',
        )
        # Parameter to do audio instead of video
        parser.add_argument(
            '--audio',
            action='store_const',
            const=True,
            help='Use if you do not want to rename audio instead of video sessions',
        )

    def handle(self, *args, **options):
        # Match session names with either an underscore or the .mp4 extension
        PATTERN = r'.*(_|\.mp4).*'
        # This is the requests session for all API calls
        REQUESTS_SESSION = create_panopto_requests_session()

        def rename_panopto_session(session_id, old_title, new_title, ask_confirmation=True):
            def _do_rename(session_id, new_title):
                url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/sessions/{u.panopto_session_id}'
                data = {
                    'Name': new_title,
                }
                response = REQUESTS_SESSION.put(url, data=data)
                return response

            if ask_confirmation:
                confirmation = input(f'Rename {old_title} to {new_title}? (y/n) ')
                if confirmation.lower() == 'y':
                    _do_rename(session_id, new_title)
            else:
                _do_rename(session_id, new_title)


        # If the audio parameter is set, change only audio uploads;
        # otherwise, change only video uploads
        if options['audio']:
            uploads = Audio.objects.all()
        else:
            uploads = Video.objects.all()

        for u in uploads:
            # Don't try to update if there is no Panopto session
            if u.panopto_session_id:
                url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/sessions/{u.panopto_session_id}'
                response = REQUESTS_SESSION.get(url)
                session_metadata = response.json()
                old_title = session_metadata.get('Name')
                # If there's an underscore or '.mp4' extension
                if re.match(PATTERN, old_title) is not None:
                    rename_panopto_session(
                        u.panopto_session_id,
                        old_title,
                        u.title,
                        not options['noconfirmation'],
                    )

            '''Get the Panopto session title'''
            '''If the title matches the pattern, rename it (possibly asking for confirmation first)'''
