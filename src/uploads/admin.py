from django.contrib import admin
from . import models

### TEXTs ###
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'type', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified')

admin.site.register(models.Text, TextAdmin)

### VIDEOs ###
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified', 'url')

admin.site.register(models.Video, VideoAdmin)

### AUDIO ###
class AudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'identifier', 'size')
    readonly_fields = ('size', 'created', 'modified', 'url')

admin.site.register(models.Audio, AudioAdmin)
