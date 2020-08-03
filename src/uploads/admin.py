from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import Upload, Video, Audio, Text

class UploadChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Upload  # Optional, explicitly set here.

@admin.register(Video)
class VideoAdmin(UploadChildAdmin):
    base_model = Video  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ('title',)
    readonly_fields = ('size', 'created', 'modified', 'url')

@admin.register(Audio)
class AudioAdmin(UploadChildAdmin):
    base_model = Audio  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ('title',)
    readonly_fields = ('size', 'created', 'modified', 'url')

@admin.register(Text)
class TextAdmin(UploadChildAdmin):
    base_model = Text  # Explicitly set here!
#    show_in_index = True  # makes child model admin visible in main admin site
    list_display = ('title',)
    readonly_fields = ('size', 'created', 'modified', 'url')

@admin.register(Upload)
class UploadParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = Upload  # Optional, explicitly set here.
    child_models = (Video, Audio, Text)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    list_display = ( 'title', 'type', 'identifier', 'created', 'modified', 'size')
    def type(self, obj):
        return obj.polymorphic_ctype
