# Generated by Django 2.2.14 on 2020-08-04 17:24

from django.db import migrations, models
import django.db.models.deletion
import uploads.models
import uploads.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=1024)),
                ('ereserves_record_url', models.URLField(blank=True, help_text='Libguides E-Reserves system record', max_length=1024, null=True)),
                ('barcode', models.CharField(blank=True, max_length=512, null=True)),
                ('form', models.CharField(choices=[('digitized', 'Digitized'), ('born_digital', 'Born Digital')], default='digitized', max_length=16)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('size', models.IntegerField(blank=True, null=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_uploads.upload_set+', to='contenttypes.ContentType')),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='mp3 format only', max_length=1024, upload_to='av/audio/', validators=[uploads.validators.validate_audio])),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='AudioAlbum',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('album_directory', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='pdf format only', max_length=1024, upload_to=uploads.models.text_upload_path, validators=[uploads.validators.validate_text])),
                ('text_type', models.CharField(choices=[('article', 'Article'), ('book_excerpt', 'Book (excerpt)'), ('book_whole', 'Book (whole)'), ('other', 'Other')], default='article', help_text='Text type cannot be changed after saving.', max_length=16)),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='mp4 format only', max_length=1024, upload_to='av/video/', validators=[uploads.validators.validate_video])),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='AudioTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(help_text='mp3 format only', max_length=1024, upload_to=uploads.models.audiotrack_upload_path, validators=[uploads.validators.validate_audio])),
                ('title', models.CharField(max_length=512)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.AudioAlbum')),
            ],
        ),
    ]
