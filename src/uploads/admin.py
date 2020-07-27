from django.contrib import admin
from . import models

class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'type', 'identifer', 'size')
    readonly_fields = ('size', 'created', 'modified')

admin.site.register(models.Text, TextAdmin)
