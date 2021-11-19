from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline, SortableStackedInline
from django.utils.safestring import mark_safe
from .models import Upload, Video, Audio, AudioAlbum, AudioTrack, Text, VttTrack, SiteSetting
from django.utils.html import format_html
from . import tasks
from django import forms
import copy
from django.utils.html import strip_tags


# This is a hacky way to set text in the admin site, but it works...
# https://stackoverflow.com/questions/4938491/django-admin-change-header-django-administration-text
admin.sites.AdminSite.site_header = 'Hitchcock Smith Libraries e-reserves administration'
admin.sites.AdminSite.site_title = 'Hitchcock Smith Libraries e-reserves administration'
admin.sites.AdminSite.site_url = None # Disable "view site" link in header
admin.sites.AdminSite.enable_nav_sidebar = False


def bytes_to_mb(byte_number):
    # If 10 MB or more, display as whole number
    if byte_number >= 10**7:
        return byte_number // (10**6)
    # If it's between 0.1 MB and 10 MB, display with one decimal place
    elif byte_number >= 10**5:
        return (byte_number // (10**5)) / 10
    # If it's less than 0.1 MB, display up to four decimal places...
    else:
        return (byte_number / (10**6))

def queue_for_processing(modeladmin, request, queryset):
    for item in queryset.all():
        tasks.upload_to_panopto(str(item.id))
        item.processing_status="Added to queue, waiting for file to be uploaded to Panopto"
        item.queued_for_processing=True
        item.save()
queue_for_processing.short_description = "(re)Process selected items"

class UploadChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """

    base_model = Upload  # Optional, explicitly set here.
    search_fields = ['title', 'barcode', 'upload', 'notes', 'ereserves_record_url']
    list_display = ( 'title', 'barcode', 'created', 'modified', 'size_in_mb', 'published')
    ordering = ('-modified',)
    list_filter = ('published',)
    actions = [queue_for_processing,]
    def size_in_mb(self, obj):
        if not obj or not obj.size:
            return None
        else:
            return bytes_to_mb(obj.size)
    size_in_mb.admin_order_field = 'size'

    class Media:
        js = ('uploads/js/uploads-admin.js',)

    def url(self, obj):
        if obj.url is not None:
            url_field = '<span id="hitchcock-url">{url}</span> &nbsp; <a href="{url}" target="_blank">view <i class="fas fa-external-link-alt" style="font-size: 12px;"></i></a> | <a href="#" id="copy-url-button">copy <i class="far fa-clipboard"></i></a>'
            field_display_string = mark_safe(url_field.format(url=obj.url))
            return field_display_string
        else:
            return '-'

class VttTrackInline(admin.TabularInline):
    model = VttTrack
    extra = 1
    exclude = ['label']

class VideoAdminForm(forms.ModelForm):
    upload_to_panopto = forms.BooleanField(required=False)

    def save(self, commit=True):
        upload_to_panopto = self.cleaned_data.get('upload_to_panopto', None)

        # Get the form instance so I can write to its fields
        instance = super(VideoAdminForm, self).save(commit=commit)

        if upload_to_panopto is True:
            tasks.upload_to_panopto(str(instance.id))
            instance.queued_for_processing = True
            instance.processing_status = "Added to queue, waiting for file to be uploaded to Panopto"

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Video
        fields = "__all__"

class AudioAdminForm(forms.ModelForm):
    upload_to_panopto = forms.BooleanField(required=False)

    def save(self, commit=True):
        upload_to_panopto = self.cleaned_data.get('upload_to_panopto', None)

        # Get the form instance so I can write to its fields
        instance = super(AudioAdminForm, self).save(commit=commit)

        if upload_to_panopto is True:
            tasks.upload_to_panopto(str(instance.id))
            instance.queued_for_processing = True
            instance.processing_status = "Added to queue, waiting for file to be uploaded to Panopto"

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Audio
        fields = "__all__"

class PanoptoUploadAdmin(NonSortableParentAdmin, UploadChildAdmin):
    readonly_fields = ['size_in_mb', 'created', 'modified', 'identifier', 'url', 'panopto_session_id', 'processing_status', 'queued_for_processing']
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            panopto_fields = [
                'upload_to_panopto',
                'panopto_session_id',
                'processing_status',
                'queued_for_processing',
            ]
        else:
            if obj.panopto_session_id is None:
                panopto_fields = [
                    'upload_to_panopto',
                    'panopto_session_id',
                    'processing_status',
                    'queued_for_processing',
                ]
            else:
                panopto_fields = [
                    'panopto_session_id',
                    'processing_status',
                    'queued_for_processing',
                ]

        fieldsets = (
            (None, {
                'fields': (
                    'title',
                    'ereserves_record_url',
                    'barcode',
                    'form',
                    'notes',
                    'published',
                    'upload',
                    'size_in_mb',
                    'created',
                    'modified',
                    'identifier',
                    'url',
                )
            }),
            ("Panopto instance", {
                'fields': panopto_fields,
            }),
        )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """Allow editing panopto_session_id when creating. But once it is set,
        by uploading a panopto session don't allow it to be edited after that.
        """
        # Make a copy of readonly_fields that doesn't have the session id field
        _ = copy.copy(self.readonly_fields)
        _.remove('panopto_session_id')
        readonly_fields_sans_panopto_session_id = _

        if obj is not None:
            if obj.lock_panopto_session_id is True:
                return self.readonly_fields
            else:
                return readonly_fields_sans_panopto_session_id
        else:
            return readonly_fields_sans_panopto_session_id

@admin.register(Video)
class VideoAdmin(PanoptoUploadAdmin):
    form = VideoAdminForm
    base_model = Video  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    inlines = [VttTrackInline,]

@admin.register(Audio)
class AudioAdmin(PanoptoUploadAdmin):
    form = AudioAdminForm
    base_model = Audio  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    # readonly_fields = ('size_in_mb', 'created', 'modified', 'identifier', 'url', 'panopto_session_id', 'processing_status', 'queued_for_processing')

class AudioAlbumInline(SortableTabularInline):
    model = AudioTrack
    extra = 1

@admin.register(AudioAlbum)
class AudioAlbumAdmin(NonSortableParentAdmin, UploadChildAdmin):
    base_model = AudioAlbum  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    readonly_fields = ('size_in_mb', 'created', 'modified', 'album_directory', 'identifier', 'url', 'queued_for_processing')
    inlines = [AudioAlbumInline,]

@admin.register(Text)
class TextAdmin(UploadChildAdmin):
    base_model = Text  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    list_display = ( 'title', 'text_type', 'barcode', 'created', 'modified', 'size_in_mb', 'published')
    readonly_fields = ('size_in_mb', 'created', 'modified', 'url', 'text_type', 'identifier', 'queued_for_processing')
    list_filter = ('published', 'text_type')
    def get_readonly_fields(self, request, obj=None):
        """If obj is None that means the object is being created. In this case
        return the normal list of readonly_fields, minus 'text_type'
        so that the user can set it durring creation. Otherwise return all of
        them, including text_type, so that the user cannot change this field
        after creation.
        """
        if obj is None:
            return ['size_in_mb', 'created', 'modified', 'identifier', 'url', 'queued_for_processing']
        else:
            return ['size_in_mb', 'created', 'modified', 'text_type', 'identifier', 'url', 'queued_for_processing']

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
    child_models = (Text, Video, Audio)
    list_filter = (
        PolymorphicChildModelFilter,
        MissingEReservesRecordFilter,
        'published',
    )
    list_display = ( 'title', 'type', 'barcode', 'created', 'modified', 'size_in_mb', 'published', 'ereserves_record')
    search_fields = ['title', 'barcode', 'ereserves_record_url', 'identifier']
    ordering = ('-modified',)
    actions = [queue_for_processing,]
    def size_in_mb(self, obj):
        if not obj or not obj.size:
            return None
        else:
            return bytes_to_mb(obj.size)
    size_in_mb.admin_order_field = 'size'

    def type(self, obj):
        return obj.polymorphic_ctype

    def ereserves_record(self, obj):
        if obj is not None:
            if obj.ereserves_record_url is not None:
                return mark_safe("<a href='%s'>record</a>" % obj.ereserves_record_url)

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def value(self, obj):
        if len(obj.setting_value) > 128:
            return strip_tags(obj.setting_value)[:128] + '...'
        else:
            return obj.setting_value

    list_display = ( 'setting_key', 'value' )
