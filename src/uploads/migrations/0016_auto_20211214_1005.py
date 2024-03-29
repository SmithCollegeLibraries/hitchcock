# Generated by Django 3.2.9 on 2021-12-14 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0015_auto_20211213_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audioplaylist',
            name='av',
            field=models.ManyToManyField(related_name='audio_playlists', through='uploads.AudioPlaylistLink', to='uploads.Audio'),
        ),
        migrations.AlterField(
            model_name='videoplaylist',
            name='av',
            field=models.ManyToManyField(related_name='video_playlists', through='uploads.VideoPlaylistLink', to='uploads.Video'),
        ),
    ]
