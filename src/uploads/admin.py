from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline, SortableStackedInline
from django.utils.safestring import mark_safe
from .models import Upload, Video, Audio, AudioAlbum, AudioTrack, Text, VideoVttTrack
from django.utils.html import format_html
from .tasks import upload_to_panopto

def queue_for_processing(modeladmin, request, queryset):
    for item in queryset.all():
        upload_to_panopto(str(item.id))
        item.processing_status="Added to queue, waiting for file to be uploaded to Panopto"
        item.queued_for_processing=True
        item.save()
queue_for_processing.short_description = "(re)Process selected items"

class UploadChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Upload  # Optional, explicitly set here.
    search_fields = ['title', 'barcode', 'ereserves_record_url']
    list_display = ( 'title', 'barcode', 'created', 'modified', 'size', 'published')
    ordering = ('-modified',)
    list_filter = ('published',)
    actions = [queue_for_processing,]

class VideoVttTrackInline(SortableTabularInline):
    model = VideoVttTrack
    extra = 1

@admin.register(Video)
class VideoAdmin(NonSortableParentAdmin, UploadChildAdmin):
    base_model = Video  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url', 'identifier', 'panopto_session_id', 'processing_status', 'queued_for_processing')
    inlines = [VideoVttTrackInline,]

@admin.register(Audio)
class AudioAdmin(UploadChildAdmin):
    base_model = Audio  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url', 'identifier', 'queued_for_processing')

class AudioAlubmInline(SortableTabularInline):
    model = AudioTrack
    extra = 1

@admin.register(AudioAlbum)
class AudioAlbumAdmin(NonSortableParentAdmin, UploadChildAdmin):
    base_model = AudioAlbum  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url', 'album_directory', 'identifier', 'queued_for_processing')
    inlines = [AudioAlubmInline,]

@admin.register(Text)
class TextAdmin(UploadChildAdmin):
    base_model = Text  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ( 'title', 'text_type', 'barcode', 'created', 'modified', 'size', 'published')
    readonly_fields = ('size', 'created', 'modified', 'url', 'text_type', 'identifier', 'queued_for_processing')
    list_filter = ('published', 'text_type')
    def get_readonly_fields(self, request, obj=None):
        """If obj is None that means the object is being created. In this case
        return the normal list of readonly_fields, minus 'text_type'
        so that the user can set it durring creation. Otherwise return all of
        them, including text_type, so that the user cannot change this field
        after creation.
        """
        if obj is None:
            return ['size', 'created', 'modified', 'url', 'identifier', 'queued_for_processing']
        else:
            return ['size', 'created', 'modified', 'url', 'text_type', 'identifier', 'queued_for_processing']

class MissingEReservesRecordFilter(admin.SimpleListFilter):
    title = "empty e-reserves url"
    parameter_name = 'E-Reserves Record'
    def lookups(self, request, model_admin):
        return (
            ('Empty', 'Empty'),
            ('Filled', 'Filled'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Empty':
            return Upload.objects.filter(ereserves_record_url__isnull=True)
        if self.value() == 'Filled':
            return Upload.objects.filter(ereserves_record_url__isnull=False)

@admin.register(Upload)
class UploadParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = Upload  # Optional, explicitly set here.
    child_models = (Video, Audio, AudioAlbum, Text)
    list_filter = (
        PolymorphicChildModelFilter,
        MissingEReservesRecordFilter,
        'published',
    )
    list_display = ( 'title', 'type', 'barcode', 'created', 'modified', 'size', 'published', 'ereserves_record')
    search_fields = ['title', 'barcode', 'ereserves_record_url', 'identifier']
    ordering = ('-modified',)
    actions = [queue_for_processing,]

    def type(self, obj):
        return obj.polymorphic_ctype

    def ereserves_record(self, obj):
        if obj is not None:
            if obj.ereserves_record_url is not None:
                return mark_safe("<a href='%s'>record</a>" % obj.ereserves_record_url)
