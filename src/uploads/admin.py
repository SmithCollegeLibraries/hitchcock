from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from .models import Upload, Video, Audio, AudioAlbum, AudioTrack, Text
from django.utils.safestring import mark_safe

class UploadChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Upload  # Optional, explicitly set here.
    search_fields = ['title', 'barcode', 'ereserves_record_url']
    list_display = ( 'title', 'barcode', 'created', 'modified', 'size', 'published')
    ordering = ('-modified',)

@admin.register(Video)
class VideoAdmin(UploadChildAdmin):
    base_model = Video  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url')

@admin.register(Audio)
class AudioAdmin(UploadChildAdmin):
    base_model = Audio  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url')

class AudioAlubmInline(admin.TabularInline):
    model = AudioTrack

@admin.register(AudioAlbum)
class AudioAlbumAdmin(UploadChildAdmin):
    base_model = AudioAlbum  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size', 'created', 'modified', 'url', 'album_directory')
    inlines = [AudioAlubmInline,]

@admin.register(Text)
class TextAdmin(UploadChildAdmin):
    base_model = Text  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ( 'title', 'text_type', 'barcode', 'created', 'modified', 'size', 'published')
    readonly_fields = ('size', 'created', 'modified', 'url', 'text_type')
    def get_readonly_fields(self, request, obj=None):
        """If obj is None that means the object is being created. In this case
        return the normal list of readonly_fields, minus 'text_type'
        so that the user can set it durring creation. Otherwise return all of
        them, including text_type, so that the user cannot change this field
        after creation.
        """
        if obj is None:
            return ['size', 'created', 'modified', 'url']
        else:
            return ['size', 'created', 'modified', 'url', 'text_type']

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
    list_filter = (PolymorphicChildModelFilter, MissingEReservesRecordFilter)
    list_display = ( 'title', 'type', 'barcode', 'created', 'modified', 'size', 'published', 'ereserves_record')
    search_fields = ['title', 'barcode', 'ereserves_record_url']
    ordering = ('-modified',)
    def type(self, obj):
        return obj.polymorphic_ctype

    def ereserves_record(self, obj):
        if obj is not None:
            if obj.ereserves_record_url is not None:
                return mark_safe("<a href='%s'>record</a>" % obj.ereserves_record_url)
