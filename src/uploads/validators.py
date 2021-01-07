import os
from django.core.exceptions import ValidationError

def validate_text(field):
    ext = os.path.splitext(field.name)[-1]
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Must be pdf.')

def validate_video(field):
    ext = os.path.splitext(field.name)[-1]
    valid_extensions = ['.mp4', '.mpeg4']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Must be mp4.')

def validate_audio(field):
    ext = os.path.splitext(field.name)[-1]
    valid_extensions = ['.mp3', '.mpeg3', '.wav']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Must be one of %s.' % ', '.join(mylist))

def validate_barcode(field):
    try:
        int(field)
    except ValueError:
        raise ValidationError('Must be numbers only.')
    if len(field) != 15:
        raise ValidationError('Must be fifteen characters long.')
