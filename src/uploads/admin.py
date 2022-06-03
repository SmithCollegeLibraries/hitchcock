import copy

from django import forms
from django.contrib import admin
from django.db import models
from django.db.models.functions import Lower
from django.db.utils import ProgrammingError
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from adminsortable2.admin import SortableInlineAdminMixin

from . import tasks
from .models import Upload, Video, Audio, Text, VttTrack, SiteSetting
from .models import Folder, Playlist, AudioPlaylist, VideoPlaylist

# This is a hacky way to set text in the admin site, but it works...
# https://stackoverflow.com/questions/4938491/django-admin-change-header-django-administration-text
admin.sites.AdminSite.site_header = 'Hitchcock administration'
admin.sites.AdminSite.site_title = 'Hitchcock administration'
admin.sites.AdminSite.site_url = None # Disable "view site" link in header
admin.sites.AdminSite.enable_nav_sidebar = False


# Allow case-insensitive searching of titles
models.CharField.register_lookup(Lower)


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
queue_for_processing.short_description = "(Re)process selected items"

def lock_panopto_id(modeladmin, request, queryset):
    for item in queryset.all():
        item.lock_panopto_session_id = True
        item.save()
lock_panopto_id.short_description = "Lock Panopto ID"

def unlock_panopto_id(modeladmin, request, queryset):
    for item in queryset.all():
        item.lock_panopto_session_id = False
        item.save()
unlock_panopto_id.short_description = "Unlock Panopto ID"

def save_update(modeladmin, request, queryset):
    for item in queryset.all():
        item.save()
save_update.short_description = "Save and update"


class UploadChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """

    base_model = Upload  # Optional, explicitly set here.
    search_fields = ['title', 'barcode', 'ereserves_record_url', 'upload', 'identifier', 'notes']
    list_display = ( 'title', 'barcode', 'created', 'modified', 'size_in_mb', 'published')
    ordering = ('-modified',)
    list_filter = ('published',)
    actions = [queue_for_processing, lock_panopto_id, unlock_panopto_id, save_update]

    # Edit the method for getting search results to allow case-insensitive
    # searching of titles
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(title__lower__contains=search_term.lower())
        return queryset, may_have_duplicates

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

class AudioInline(SortableInlineAdminMixin, admin.TabularInline):
    # We use the juction model specified on AudioPlaylist.
    # https://django-admin-sortable2.readthedocs.io/en/latest/usage.html
    model = AudioPlaylist.av.through
    # Autocomplete: https://stackoverflow.com/a/67905237/2569052
    autocomplete_fields = ['av']

class VideoInline(SortableInlineAdminMixin, admin.TabularInline):
    # We use the juction model specified on VideoPlaylist.
    # https://django-admin-sortable2.readthedocs.io/en/latest/usage.html
    model = VideoPlaylist.av.through
    # Autocomplete: https://stackoverflow.com/a/67905237/2569052
    autocomplete_fields = ['av']

class VideoAdminForm(forms.ModelForm):
    upload_to_panopto = forms.BooleanField(label='Upload to Panopto', required=False, initial=True)

    def save(self, commit=True):
        upload_to_panopto = self.cleaned_data.get('upload_to_panopto', None)
        # Get the form instance so I can write to its fields
        instance = super().save(commit=commit)
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
    upload_to_panopto = forms.BooleanField(initial=True, required=False)

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

class PanoptoUploadAdmin(UploadChildAdmin):
    readonly_fields = [
        'size_in_mb',
        'created',
        'modified',
        'identifier',
        'url',
        'panopto_session_id',
        'processing_status',
        'queued_for_processing',
    ]
    def get_fieldsets(self, request, obj=None):
        basic_fields = [
            'title',
            'form',
            'upload',
            'published',
        ]
        if obj is None or not obj.processing_status:
            basic_fields.append('upload_to_panopto')
        # Hide the Folder field unless there is more than one
        try:
            if Folder.objects.all().count() > 1:
                basic_fields.append('folder')
        except ProgrammingError:
            pass
        basic_fields.append('url')
        basic_fields.append('notes')

        panopto_fields = [
            'panopto_session_id',
            'processing_status',
            'queued_for_processing',
            'description',
        ]

        fieldsets = (
            (None, {
                'fields': basic_fields
            }),
            ('Panopto', {
                'fields': panopto_fields,
            }),
            ('Details', {
                'classes': ('collapse',),
                'fields': (
                    'identifier',
                    'ereserves_record_url',
                    'barcode',
                    'size_in_mb',
                    'created',
                    'modified',
                ),
            }),
        )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """Allow editing panopto_session_id when creating. But once it
        is set after a Panopto upload is complete, don't allow it to be
        edited after that.

        Allow changing a folder as long as an upload is not actively
        in process.
        """
        # Make a copy of readonly_fields that doesn't have the session id field
        _ = copy.copy(self.readonly_fields)
        _.remove('panopto_session_id')
        readonly_fields_sans_panopto_session_id = _

        if obj is not None:
            if obj.lock_panopto_session_id is True:
                new_readonly_fields = self.readonly_fields
            else:
                new_readonly_fields = readonly_fields_sans_panopto_session_id

            # Now add folder to the list of readonly fields if an upload
            # is actively underway (i.e. it has started processing but
            # there is not yet a session ID)
            if not obj.processing_status and not obj.panopto_session_id:
                new_readonly_fields.append('folder')
            return new_readonly_fields

        else:
            return readonly_fields_sans_panopto_session_id


@admin.register(Video)
class VideoAdmin(PanoptoUploadAdmin):
    form = VideoAdminForm
    base_model = Video  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site
    inlines = [VttTrackInline]

@admin.register(Audio)
class AudioAdmin(PanoptoUploadAdmin):
    form = AudioAdminForm
    base_model = Audio  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site

@admin.register(Text)
class TextAdmin(UploadChildAdmin):
    base_model = Text  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ('title', 'text_type', 'barcode', 'created', 'modified', 'size_in_mb', 'published')
    readonly_fields = ('size_in_mb', 'created', 'modified', 'url', 'text_type', 'identifier')
    fieldsets = (
        (None, {
            'fields': ('title',
                       'form',
                       'text_type',
                       'upload',
                       'published',
                       'url',
                       # 'description',
                       'notes',
                      ),
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('identifier', 'ereserves_record_url', 'barcode', 'size_in_mb', 'modified', 'created'),
        }),
    )
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



class PlaylistAdmin(PolymorphicChildModelAdmin):
    base_model = Playlist
    show_in_index = False
    list_display = ('title', 'panopto_playlist_id')
    readonly_fields = ('panopto_playlist_id', 'url', 'created', 'modified')
    list_filter = ('title', 'panopto_playlist_id')

    basic_fields = [
        'title',
        'published',
    ]
    # Hide the Folder field unless there is more than one
    try:
        if Folder.objects.all().count() > 1:
            basic_fields.append('folder')
    except ProgrammingError:
        pass
    basic_fields.append('url')
    basic_fields.append('notes')

    fieldsets = (
        (None, {
            'fields': basic_fields,
        }),
        ('Panopto', {
            'fields': (
                'panopto_playlist_id',
                'description',
            ),
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': (
                'created',
                'modified',
            ),
        }),
    )

    class Media:
        js = ('uploads/js/uploads-admin.js',)

    def url(self, obj):
        if obj.url is not None:
            url_field = '<span id="hitchcock-url">{url}</span> &nbsp; <a href="{url}" target="_blank">view <i class="fas fa-external-link-alt" style="font-size: 12px;"></i></a> | <a href="#" id="copy-url-button">copy <i class="far fa-clipboard"></i></a>'
            field_display_string = mark_safe(url_field.format(url=obj.url))
            return field_display_string
        else:
            return '-'


@admin.register(AudioPlaylist)
class AudioPlaylistAdmin(PlaylistAdmin):
    base_model = AudioPlaylist
    show_in_index = True  # makes child model admin visible in main admin site
    inlines = [AudioInline]

    # Change the saving behavior so that the inline playlist links
    # get saved *before* the playlist itself.
    # https://stackoverflow.com/a/35140131/2569052
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Call super method if object has no primary key
            super().save_model(request, obj, form, change)
        else:
            pass  # Don't actually save the parent instance

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        super().save_model(request, form.instance, form, change)


@admin.register(VideoPlaylist)
class VideoPlaylistAdmin(PlaylistAdmin):
    base_model = VideoPlaylist
    show_in_index = True  # makes child model admin visible in main admin site
    inlines = [VideoInline]

    # Change the saving behavior so that the inline playlist links
    # get saved *before* the playlist itself.
    # https://stackoverflow.com/a/35140131/2569052
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Call super method if object has no primary key
            super().save_model(request, obj, form, change)
        else:
            pass  # Don't actually save the parent instance

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        super().save_model(request, form.instance, form, change)


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
    search_fields = ['title', 'barcode', 'ereserves_record_url', 'identifier', 'notes']
    ordering = ('-modified',)
    actions = [queue_for_processing, save_update]

    # Edit the method for getting search results to allow case-insensitive
    # searching of titles
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(title__lower__contains=search_term.lower())
        return queryset, may_have_duplicates

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

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'panopto_folder_id', 'notes')
    list_display = ('name', 'id', 'panopto_folder_id')
    readonly_fields = ('id',)

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def value(self, obj):
        if len(obj.setting_value) > 128:
            return strip_tags(obj.setting_value)[:128] + '...'
        else:
            return obj.setting_value

    list_display = ( 'setting_key', 'value' )
