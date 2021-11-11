# Generated by Django 3.2.9 on 2021-11-10 16:15

from django.db import migrations, models
import django.db.models.deletion
import uploads.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('uploads', '0012_auto_20211105_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vtttrack',
            name='upload',
            field=models.FileField(help_text='vtt format only', max_length=1024, upload_to='av/vtt/', validators=[uploads.validators.validate_captions]),
        ),
    ]