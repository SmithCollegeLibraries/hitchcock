from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from . import models

class HitchcockAdminSite(admin.AdminSite):
    site_header = 'Hitchcock Smith Libraries e-reserves administration'
    site_title = 'Hitchcock Smith Libraries e-reserves administration'
    site_url = None

hitchcock_admin = HitchcockAdminSite(name='hitchcockadmin')

### TEXTs ###
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'type', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified', 'url')

hitchcock_admin.register(models.Text, TextAdmin)

### VIDEOs ###
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified', 'url')

hitchcock_admin.register(models.Video, VideoAdmin)

### AUDIO ###
class AudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified', 'url')

hitchcock_admin.register(models.Audio, AudioAdmin)


#@hitchcock_admin.register(models.Upload)
class ModelAParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.Upload  # Optional, explicitly set here.
    child_models = (models.Text, models.Video, models.Audio)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    list_display = ('title', 'identifier')
hitchcock_admin.register(models.Upload, ModelAParentAdmin)
