from django.db import models
from django.dispatch import receiver
import os

# Video i.e. mp4
# Audio i.e. mp3
# Text i.e. pdf
def text_upload_path(instance, filename):
    """Calculate the appropriate path to upload text files to, depending
    on the type chosen for the given text upload. So that they are easier
    to manage on the filesystem.
    """
    lookup = {
        'article': 'articles/',
        'book_excerpt': 'books-excerpt/',
        'book_whole': 'books-whole/',
        'other': 'other',
    }
    # Reimpliment filename sanitization, and collision avoidance
    storage = instance.upload.storage
    valid_filename = storage.get_valid_name(filename)
    proposed_path = 'text/' + lookup[instance.type] + valid_filename
    available_filename = storage.get_available_name(proposed_path)
    return available_filename

class Text(models.Model):
    upload = models.FileField(upload_to=text_upload_path, max_length=512)
    TEXT_TYPES = [
        ('article', 'Article'),
        ('book_excerpt', 'Book (excerpt)'),
        ('book_whole', 'Book (whole)'),
        ('other', 'Other'),
    ]
    FORM_TYPES = [
        ('digitized', 'Digitized'),
        ('born_digital', 'Born Digital'),
    ]
    
    title = models.CharField(max_length=1024)
    identifer = models.CharField(max_length=512, help_text='barcode, ISBN, etc.')
    type = models.CharField(max_length=16, choices=TEXT_TYPES, default='article')
    form = models.CharField(max_length=16, choices=FORM_TYPES, default='digitized')
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    @property
    def name(self):
        if self.upload.name is not None:
            return self.upload.name.split('/')[-1]
        else:
            return None
    @property
    def size(self):
        """Return size in MB
        """
        return '%0.2fMB' % (self.upload.size/1000000)

    def __str__(self):
        return self.upload.name

@receiver(models.signals.post_delete, sender=Text)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Text` object is deleted.
    """
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)
