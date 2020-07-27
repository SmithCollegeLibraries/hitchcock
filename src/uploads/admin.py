from django.contrib import admin
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
