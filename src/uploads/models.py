from django.db import models
from polymorphic.models import PolymorphicModel
from django.dispatch import receiver
from django.conf import settings
from .validators import validate_video, validate_audio, validate_text, validate_barcode
from django.core.files.storage import DefaultStorage
from django.db.models.query_utils import DeferredAttribute
from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from .tasks import upload_to_panopto
from .codes import ISO_LANGUAGE_CODES
import uuid
import os

class Upload(PolymorphicModel):
    """ Generic "Upload" model for subclassing to the content specific models.
    """
    FORM_TYPES = [
        ('digitized', 'Digitized'),
        ('born_digital', 'Born Digital'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=1024, blank=True, null=True)
    title = models.CharField(max_length=1024)
    ereserves_record_url = models.URLField(max_length=1024, help_text="Libguides E-Reserves system record", blank=True, null=True)
    barcode = models.CharField(max_length=512, blank=True, null=True, validators=[validate_barcode,])
    form = models.CharField(max_length=16, choices=FORM_TYPES, default='digitized')
    notes = models.TextField(blank=True, null=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(blank=True, null=True)
    published = models.BooleanField(default=False)
    queued_for_processing = models.BooleanField(default=False)
    @property
    def name(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]
        else:
            return None
    # @property
    # def size(self):
    #     """Return size in MB
    #     """
    #     return '%0.2fMB' % (self.upload.size/1000000)

    def __str__(self):
        return self.title

### Text i.e. pdf ###
def text_upload_path(instance, filename):
    """Calculate the appropriate path to upload text files to, depending
    on the type chosen for the given text upload. So that they are easier
    to manage on the filesystem.
    """
    lookup = {
        'article': 'articles/',
        'book_excerpt': 'books-excerpt/',
        'book_whole': 'books-whole/',
        'other': 'other',
    }
    # Reimpliment filename sanitization, and collision avoidance
    storage = instance.upload.storage
    valid_filename = storage.get_valid_name(filename)
    proposed_path = settings.TEXT_SUBDIR_NAME + lookup[instance.text_type] + valid_filename
    available_filename = storage.get_available_name(proposed_path)
    return available_filename

class Text(Upload):
    upload = models.FileField(
        upload_to=text_upload_path,
        max_length=1024,
        validators=[validate_text,],
        help_text="pdf format only"
    )
    TEXT_TYPES = [
        ('article', 'Article'),
        ('book_excerpt', 'Book (excerpt)'),
        ('book_whole', 'Book (whole)'),
        ('other', 'Other'),
    ]

    text_type = models.CharField(max_length=16, choices=TEXT_TYPES, default='article', help_text="Text type cannot be changed after saving.")

    @property
    def url(self):
        if self.created is not None:
            return settings.BASE_URL + "/texts/%s" % self.id
        else:
            return None
    @property
    def stream_url(self):
        if self.created is not None:
            return settings.TEXTS_ENDPOINT + self.upload.name.replace(settings.TEXT_SUBDIR_NAME, '')
        else:
            return None

### Video i.e. mp4 ###
class Video(Upload):
    upload = models.FileField(
        upload_to=settings.AV_SUBDIR_NAME + 'video/',
        max_length=1024,
        validators=[validate_video,],
        help_text="mp4 format only")
    panopto_session_id = models.CharField(max_length=256, blank=True, null=True)
    processing_status = models.CharField(max_length=256, blank=True, null=True)

    @property
    def url(self):
        if self.created is not None:
            return settings.BASE_URL + "/videos/%s" % self.id
        else:
            return None

@receiver(models.signals.post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        upload_to_panopto(str(instance.id))
        instance.queued_for_processing = True
        instance.processing_status = "Added to queue, waiting for file to be uploaded to Panopto"
        instance.save()

class VideoVttTrack(SortableMixin):
    class Meta:
        ordering = ['vtt_order']

    TEXT_TRACK_TYPES = [
        ('captions', 'Captions (for hearing impairment)'),
        ('subtitles', 'Subtitles (for language translations)'),
        ('descriptions', 'Descriptions (for vision impairment)'),
        # ('chapters', 'Chapters'),
        # ('metadata', 'Metadata (for machines, not humans)'),
    ]
    upload = models.FileField(
        upload_to=settings.TEXT_SUBDIR_NAME + settings.VTT_SUBDIR_NAME,
        max_length=1024,
#        validators=[validate_audio,],
        help_text="vtt format only")
    type = models.CharField(max_length=16, choices=TEXT_TRACK_TYPES)
    language = models.CharField(
        max_length=2,
        choices=ISO_LANGUAGE_CODES,
        default='en'
    )
    label = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        help_text="Optional - Users see this. Overrides the name in the user interface generated from the Type and Language fields. Don't use this unless you know what you are doing."
    )
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    video = SortableForeignKey(Video, on_delete=models.CASCADE)
    vtt_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]

    @property
    def stream_url(self):
        if self.created is not None:
            return settings.TEXTS_ENDPOINT + self.upload.name.replace(settings.TEXT_SUBDIR_NAME, '')
        else:
            return None

# Audio i.e. mp3
class Audio(Upload):
    upload = models.FileField(
        upload_to=settings.AV_SUBDIR_NAME + 'audio/',
        max_length=1024,
        validators=[validate_audio,],
        help_text="mp3 format only")
    def url(self):
        print(type(self.created))
        if self.created is not None:
            return settings.BASE_URL + "/audio/%s" % self.id
        else:
            return None

class AudioAlbum(Upload):
    album_directory = models.CharField(max_length=512, blank=True, null=True)
    
    def url(self):
        if self.created is not None:
            return settings.BASE_URL + "/audio-album/%s" % self.id
        else:
            return None

@receiver(models.signals.pre_save, sender=AudioAlbum)
def set_album_directory(sender, instance, **kwargs):
    """
    Sets the album_directory field for a newly created AudioAlbum object.
    Does not run after creation. I.e. this field cannot be changed after
    the object is saved. Cheap way to make it so that the user can make minor
    changes to the title after saving without accidentally altering the
    target album dir.
    """
    if instance.album_directory is None:
        storage = DefaultStorage()
        valid_filename = storage.get_valid_name(instance.title)
        proposed_path = settings.AUDIO_ALBUMS_SUBDIR_NAME + valid_filename
        available_filename = storage.get_available_name(proposed_path)
        instance.album_directory = available_filename

@receiver(models.signals.post_delete, sender=AudioAlbum)
def auto_delete_album_on_delete(sender, instance, **kwargs):
    """
    Delete empty album directory on delete of the corresponding object
    """
    if instance.album_directory is not None:
        album_directory = settings.MEDIA_ROOT + '/' + instance.album_directory
        print("Deleting the dir %s" % album_directory)
        if os.path.isdir(album_directory):
            os.rmdir(album_directory)

def audiotrack_upload_path(instance, filename):
    # Get parent album upload directory
    base_path = instance.album.album_directory
    # Reimpliment filename sanitization, and collision avoidance
    storage = instance.upload.storage
    valid_filename = storage.get_valid_name(filename)
    proposed_path = base_path + '/' + valid_filename
    available_filename = storage.get_available_name(proposed_path)
    return available_filename

class AudioTrack(SortableMixin):
    class Meta:
        ordering = ['track_order']

    upload = models.FileField(
        upload_to=audiotrack_upload_path,
        max_length=1024,
        validators=[validate_audio,],
        help_text="mp3 format only")
    title = models.CharField(max_length=512)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    album = SortableForeignKey(AudioAlbum, on_delete=models.CASCADE)
    track_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]

@receiver(models.signals.pre_save, sender=AudioTrack)
def update_album_size(sender, instance, **kwargs):
    """
    Update album size calculation after each time a track is saved or updated.
    """
    sum_size = 0
    try:
        new_track_size = instance.upload.size
    except FileNotFoundError:
        new_track_size = 0
    sum_size += new_track_size
    existing_tracks = instance.album.audiotrack_set.all()
    for track in existing_tracks:
        try:
            track_size = track.upload.size
        except FileNotFoundError:
            track_size = 0
        sum_size += track_size
    instance.album.size = sum_size
    instance.album.save()
        

@receiver(models.signals.post_delete, sender=AudioTrack)
def auto_delete_track_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Upload` object is deleted.
    """
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)

    # AND update album total size
    update_album_size(sender, instance, **kwargs)

# Handle deletion
@receiver(models.signals.post_delete, sender=Text)
@receiver(models.signals.post_delete, sender=Video)
@receiver(models.signals.post_delete, sender=Audio)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Upload` object is deleted.
    """
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)

# Calculate size and save it to the parent Upload object
@receiver(models.signals.pre_save, sender=Text)
@receiver(models.signals.pre_save, sender=Video)
@receiver(models.signals.pre_save, sender=Audio)
def update_upload_size(sender, instance, **kwargs):
    """Saves the file size to the Upload model
    """
    instance.size = instance.upload.size

@receiver(models.signals.pre_save, sender=Text)
@receiver(models.signals.pre_save, sender=Video)
@receiver(models.signals.pre_save, sender=Audio)
@receiver(models.signals.pre_save, sender=AudioAlbum)
def update_upload_identifier(sender, instance, **kwargs):
    """Saves a text copy of the ID to a field for searching on
    """
    instance.identifier = str(instance.id)
