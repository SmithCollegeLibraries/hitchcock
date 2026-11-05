from django.core.management.base import BaseCommand

from uploads.models import Upload
from uploads.management.commands.create_uploads_from_csv import get_location_of_file, add_upload_to_database, is_audio, is_video


class Command(BaseCommand):
    help = '''Provide a list of IDs to delete'''

    def add_arguments(self, parser):
        parser.add_argument('id_list', nargs='+', type=str)

    def handle(self, *args, **options):
        for id in options['id_list']:
            try:
                upload_to_delete = Upload.objects.get(id=id)
                upload_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted upload with ID {id}: {upload_to_delete.title}'))
            except Upload.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Upload with ID {id} does not exist'))
