import uuid
import os
import requests

from django.core.files.storage import DefaultStorage
from django.db import models
from django.db.models.query_utils import DeferredAttribute
from django.dispatch import receiver
from django.conf import settings
from model_utils import FieldTracker
from polymorphic.models import PolymorphicModel
from .panopto.panopto_oauth2 import PanoptoOAuth2
from .validators import validate_video, validate_audio, validate_text, validate_barcode, validate_captions


def create_panopto_requests_session(skip_verify=False):
    oauth2 = PanoptoOAuth2(settings.PANOPTO_SERVER, settings.PANOPTO_CLIENT_ID, settings.PANOPTO_CLIENT_SECRET, not skip_verify, settings.PANOPTO_AUTH_CACHE_FILE_PATH)
    requests_session = requests.Session()
    requests_session.verify = not skip_verify
    access_token = oauth2.get_access_token_authorization_code_grant()
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})
    return requests_session


class Upload(PolymorphicModel):
    """ Generic "Upload" model for subclassing to the content specific models.
    """
    FORM_TYPES = [
        ('digitized', 'Digitized'),
        ('born_digital', 'Born Digital'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=1024, blank=True, null=True)
    title = models.CharField(max_length=255, unique=True)
    ereserves_record_url = models.URLField(max_length=1024, help_text="Libguides E-Reserves system record", blank=True, null=True)
    barcode = models.CharField(max_length=512, blank=True, null=True, validators=[validate_barcode])
    form = models.CharField(max_length=16, choices=FORM_TYPES, default='digitized')
    notes = models.TextField(blank=True, null=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField(blank=True, null=True)
    published = models.BooleanField(default=True)
    queued_for_processing = models.BooleanField(default=False)
    @property
    def name(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]
        else:
            return None
    @property
    def reference_number(self):
        """Generate a shorter version of the ID for use by users when refering
        to objects in the system. Useful for reading over the phone. Still works
        when searching in the Admin interface.

        Turns this: 97070806-f73f-401b-8280-d19161e6749a
        Into this: 97070806
        """
        return self.identifier.split('-')[0]

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("view_inventory", "Can view non-staff inventory of materials (for faculty)"),
        ]
        verbose_name_plural = "Uploads (all types)"

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
        'other': 'other/',
    }
    # Reimplement filename sanitization, and collision avoidance
    storage = instance.upload.storage
    valid_filename = storage.get_valid_name(filename)
    proposed_path = settings.TEXT_SUBDIR_NAME + lookup[instance.text_type] + valid_filename
    available_filename = storage.get_available_name(proposed_path)
    return available_filename

class Text(Upload):
    upload = models.FileField(
        upload_to=text_upload_path,
        max_length=1024,
        validators=[validate_text],
        help_text="pdf format only"
    )
    TEXT_TYPES = [
        ('article', 'Article'),
        ('book_excerpt', 'Book (excerpt)'),
        ('book_whole', 'Book (whole)'),
        ('other', 'Other'),
    ]

    text_type = models.CharField(max_length=16, choices=TEXT_TYPES, help_text="Text type cannot be changed after saving.")
    tracker = FieldTracker()

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
        validators=[validate_video],
        help_text="mp4 format only")
    panopto_session_id = models.CharField(max_length=256, blank=True, null=True)
    processing_status = models.CharField(max_length=256, blank=True, null=True)
    lock_panopto_session_id = models.BooleanField(default=False)
    tracker = FieldTracker()

    @property
    def url(self):
        if self.created is not None:
            return settings.BASE_URL + "/videos/%s" % self.id
        else:
            return None

### Subtitle or caption file i.e. vtt ###
class VttTrack(models.Model):
    class Meta:
        ordering = ['vtt_order']

    VTT_TRACK_TYPES = [
        ('subtitles', 'Subtitles (for language translations)'),
        ('captions', 'Captions (for Deaf and hard-of-hearing users)'),
        ('descriptions', 'Descriptions (for vision impairment)'),
        # ('chapters', 'Chapters'),
        # ('metadata', 'Metadata (for machines, not humans)'),
    ]

    PANOPTO_LANGUAGES = [
        ('English_USA', 'English (United States)'),
        ('English_GBR', 'English (United Kingdom)'),
        ('English_AUS', 'English (Australia)'),
        ('Spanish_MEX', 'Spanish (Mexico)'),
        ('Spanish_ESP', 'Spanish (Spain)'),
        ('Chinese_Simplified', 'Chinese (Simplified)'),
        ('Chinese_Traditional', 'Chinese (Traditional)'),
        ('Danish', 'Danish'),
        ('Dutch', 'Dutch'),
        ('Finnish', 'Finnish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Hungarian', 'Hungarian'),
        ('Italian', 'Italian'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Norwegian', 'Norwegian'),
        ('Polish', 'Polish'),
        ('Portuguese', 'Portuguese'),
        ('Russian', 'Russian'),
        ('Swedish', 'Swedish'),
        ('Thai', 'Thai'),
    ]

    upload = models.FileField(
        upload_to=settings.AV_SUBDIR_NAME + settings.VTT_SUBDIR_NAME,
        max_length=1024,
        validators=[validate_captions],
        help_text="vtt format only",
    )
    type = models.CharField(
        max_length=20,
        choices=VTT_TRACK_TYPES,
    )
    language = models.CharField(
        max_length=20,
        choices=PANOPTO_LANGUAGES,
        default='English_USA'
    )
    label = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        help_text="Optional - Users see this. Overrides the name in the user interface generated from the Type and Language fields. Don't use this unless you know what you are doing."
    )
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    vtt_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    tracker = FieldTracker()

    def upload_captions(self, requests_session=None):
        '''Upload captions using API request and return response object.'''
        if not requests_session:
            requests_session = create_panopto_requests_session()
        panopto_session_id = self.video.panopto_session_id
        # Only try to upload captions if there's a session id to attach it to
        if panopto_session_id:
            filename = os.path.split(self.upload.name)[1]
            url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/sessions/{panopto_session_id}/captions'
            files = {'file': (filename, self.upload.file.open('rb').read())}
            data = {'language': self.language}
            response = requests_session.post(url, data=data, files=files)
            return response

    def __str__(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]

    @property
    def stream_url(self):
        if self.created is not None:
            return settings.TEXTS_ENDPOINT + self.upload.name.replace(settings.TEXT_SUBDIR_NAME, '')
        else:
            return None

# Audio i.e. mp3, m4a, or wav
class Audio(Upload):
    upload = models.FileField(
        upload_to=settings.AV_SUBDIR_NAME + 'audio/',
        max_length=1024,
        validators=[validate_audio],
        help_text="mp3, m4a or wav")
    panopto_session_id = models.CharField(max_length=256, blank=True, null=True)
    processing_status = models.CharField(max_length=256, blank=True, null=True)
    lock_panopto_session_id = models.BooleanField(default=False)
    tracker = FieldTracker()

    @property
    def url(self):
        if self.created is not None:
            return settings.BASE_URL + "/audio/%s" % self.id
        else:
            return None


class Playlist(PolymorphicModel):
    title = models.CharField(max_length=512)
    panopto_playlist_id = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title if self.title else 'Unnamed Playlist'

    def delete_panopto_playlist(self, requests_session=None):
        '''Delete Panopto playlist associated with playlist in Hitchcock.'''
        if not requests_session:
            requests_session = create_panopto_requests_session()
        panopto_playlist_id = self.panopto_playlist_id
        url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/playlists/{panopto_playlist_id}'
        response = requests_session.delete(url)
        print("Deleting Panopto playlist")
        print(response)
        return response

    def update_playlist_details(self, requests_session=None):
        '''Update the title of a playlist on Panopto'''
        if self.panopto_playlist_id:
            if not requests_session:
                requests_session = create_panopto_requests_session()
            url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/playlists/{self.panopto_playlist_id}'
            data = {
                'Name': self.title,
            }
            response = requests_session.put(url, data=data)
            return response
        # This method shouldn't be called if there is no playlist ID
        else:
            return


class AudioPlaylist(Playlist):
    tracker = FieldTracker()
    av = models.ManyToManyField(Audio, through='AudioPlaylistLink')

    def refresh_playlist_items(self, requests_session=None):
        '''Removes all the items from the playlist and adds them
        all back again in the proper order.
        '''
        # Delete everything from playlist
        for i in AudioPlaylistLink.objects.filter(playlist=self):
            i.delete_from_panopto_playlist(requests_session=requests_session)
        # Re-add everything to playlist
        for i in AudioPlaylistLink.objects.filter(playlist=self).order_by('playlist_order'):
            i.add_to_panopto_playlist(requests_session=requests_session)


class VideoPlaylist(Playlist):
    tracker = FieldTracker()
    av = models.ManyToManyField(Video, through='VideoPlaylistLink')

    def refresh_playlist_items(self, requests_session=None):
        '''Removes all the items from the playlist and adds them
        all back again in the proper order.
        '''
        # Delete everything from playlist
        for i in VideoPlaylistLink.objects.filter(playlist=self):
            i.delete_from_panopto_playlist(requests_session=requests_session)
        # Re-add everything to playlist
        for i in VideoPlaylistLink.objects.filter(playlist=self):
            i.add_to_panopto_playlist(requests_session=requests_session)


class PlaylistLink(PolymorphicModel):
    playlist_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{str(self.playlist)} - {str(self.playlist_order)}. {str(self.av)}'

    def add_to_panopto_playlist(self, requests_session=None):
        '''Add to playlist using API request.'''
        if not requests_session:
            requests_session = create_panopto_requests_session()
        panopto_playlist_id = self.playlist.panopto_playlist_id
        panopto_session_id = self.av.panopto_session_id
        # Only try to add to playlist if there's a playlist and a session
        if panopto_playlist_id and panopto_session_id:
            url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/playlists/{panopto_playlist_id}/sessions'
            data = {'SessionId': self.av.panopto_session_id}
            response = requests_session.put(url, data=data)
            return response
        else:
            print("Didn't add to playlist -- at least yet")

    def delete_from_panopto_playlist(self, requests_session=None):
        '''Delete from playlist using API request.'''
        if not requests_session:
            requests_session = create_panopto_requests_session()
        panopto_playlist_id = self.playlist.panopto_playlist_id
        panopto_session_id = self.av.panopto_session_id
        url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/playlists/{panopto_playlist_id}/sessions/{panopto_session_id}'
        response = requests_session.delete(url)
        return response


class AudioPlaylistLink(PlaylistLink):
    class Meta:
        ordering = ['playlist_order']
        unique_together = ['av', 'playlist']

    av = models.ForeignKey(Audio, on_delete=models.CASCADE)
    playlist = models.ForeignKey(AudioPlaylist, on_delete=models.CASCADE)
    tracker = FieldTracker()


class VideoPlaylistLink(PlaylistLink):
    class Meta:
        ordering = ['playlist_order']
        unique_together = ['av', 'playlist']

    av = models.ForeignKey(Video, on_delete=models.CASCADE)
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.CASCADE)
    tracker = FieldTracker()


class SiteSetting(models.Model):
    """A place in the database for miscellaneous settings that are configurable
    by a staff administrator role. E.g. Text blocks that appear throughout the
    site, API keys, or other settings.
    """
    setting_key = models.CharField(max_length=512)
    setting_value = models.TextField()

    def __str__(self):
        return self.setting_key

# Delete file from server if Hitchcock entry is deleted
@receiver(models.signals.post_delete, sender=Text)
@receiver(models.signals.post_delete, sender=Video)
@receiver(models.signals.post_delete, sender=Audio)
@receiver(models.signals.post_delete, sender=VttTrack)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Upload` object is deleted.
    """
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)

# Delete old file if the file has changed
@receiver(models.signals.post_save, sender=Text)
@receiver(models.signals.post_save, sender=Video)
@receiver(models.signals.post_save, sender=Audio)
@receiver(models.signals.post_save, sender=VttTrack)
def delete_previous_upload(sender, instance, **kwargs):
    """Checks the old file against the new file, and if it has
    changed, deletes the old file.
    """
    previous_upload = instance.tracker.previous('upload')
    if previous_upload:
        if instance.upload.path != previous_upload.path:
            os.remove(instance.tracker.previous('upload').path)

# Add tag to Panopto session when Hitchcock entry is deleted
@receiver(models.signals.post_delete, sender=Video)
@receiver(models.signals.post_delete, sender=Audio)
def tag_panopto_session_on_delete(sender, instance, skip_verify=False, **kwargs):
    """Adds `deleted-from-hitchcock` tag to Panopto sessions upon
    deletion of the upload in Hitchcock.
    """
    if instance.panopto_session_id:
        requests_session = create_panopto_requests_session()

        url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/sessions/{instance.panopto_session_id}/tags'
        existing_tags = requests_session.get(url)
        # If the session has been deleted, this will return an error,
        # in which case we should not be adding another tag.
        if not existing_tags.ok:
            return existing_tags
        else:
            tags = [t["Content"] for t in existing_tags.json()]
            tags.append('deleted-from-hitchcock')
            data = {'Tags': tags}
            response = requests_session.put(url, data=data)
            return response

# Calculate size and save it to the parent Upload object
@receiver(models.signals.pre_save, sender=Text)
@receiver(models.signals.pre_save, sender=Video)
@receiver(models.signals.pre_save, sender=Audio)
@receiver(models.signals.pre_save, sender=VttTrack)
def update_upload_size(sender, instance, **kwargs):
    """Saves the file size to the Upload model"""
    instance.size = instance.upload.size

@receiver(models.signals.pre_save, sender=Text)
@receiver(models.signals.pre_save, sender=Video)
@receiver(models.signals.pre_save, sender=Audio)
def update_upload_identifier(sender, instance, **kwargs):
    """Saves a text copy of the ID to a field for searching on"""
    instance.identifier = str(instance.id)

@receiver(models.signals.post_save, sender=VttTrack)
def update_caption_uploads(sender, instance, **kwargs):
    """Adds the captions to the Panopto session"""
    instance.upload_captions()

@receiver(models.signals.post_save, sender=AudioPlaylist)
@receiver(models.signals.post_save, sender=VideoPlaylist)
def create_or_refresh_playlist(sender, instance, created, **kwargs):
    """Removes all the previous items on the playlist, and
    uploads all the new ones. Every time a playlist is saved,
    the whole Panopto playlist is recreated from scratch.
    If the playlist is brand new, first create the playlist.
    """
    requests_session = create_panopto_requests_session()
    if created:
        url = f'https://{settings.PANOPTO_SERVER}/Panopto/api/v1/playlists'
        data = {
            'Name': instance.title,
            'Description': '',  # Could add a description field later
            'FolderId': settings.PANOPTO_FOLDER_ID,
            'Sessions': [],  # We will add the sessions later
        }
        response = requests_session.post(url, data=data)
        instance.panopto_playlist_id = response.json()['Id']
        instance.save()  # This will trigger the refresh post-save
    else:
        # Updates the playlist title on Panopto if necessary
        if instance.tracker.previous('title') and instance.tracker.previous('title') != instance.title:
            instance.update_playlist_details(requests_session=requests_session)
        instance.refresh_playlist_items(requests_session=requests_session)

@receiver(models.signals.post_delete, sender=AudioPlaylist)
@receiver(models.signals.post_delete, sender=VideoPlaylist)
def remove_panopto_playlist(sender, instance, **kwargs):
    """Whenever a playlist is deleted in Hitchcock, the related
    playlist in Panopto needs to be deleted as well.
    """
    instance.delete_panopto_playlist()

@receiver(models.signals.post_delete, sender=AudioPlaylistLink)
@receiver(models.signals.post_delete, sender=VideoPlaylistLink)
def remove_deleted_item_from_playlist(sender, instance, **kwargs):
    """Whenever an audio/video is taken off a playlist, the link
    between them is deleted. This needs to be reflected in the
    Panopto playlist as well.
    """
    # Don't try to remove from Panopto playlist if the playlist
    # has already been deleted
    if instance.playlist is not None:
        instance.delete_from_panopto_playlist()
