# Generated by Django 3.2.9 on 2021-11-22 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0013_auto_20211110_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioPlaylist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('panopto_playlist_id', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AudioPlaylistLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_order', models.PositiveIntegerField(default=0)),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.audio')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.audioplaylist')),
            ],
            options={
                'ordering': ['playlist_order'],
                'unique_together': {('audio', 'playlist')},
            },
        ),
        migrations.CreateModel(
            name='VideoPlaylist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('panopto_playlist_id', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoPlaylistLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_order', models.PositiveIntegerField(default=0)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.videoplaylist')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.video')),
            ],
            options={
                'ordering': ['playlist_order'],
                'unique_together': {('video', 'playlist')},
            },
        ),
        migrations.RemoveField(
            model_name='audiotrack',
            name='album',
        ),
        migrations.DeleteModel(
            name='AudioAlbum',
        ),
        migrations.DeleteModel(
            name='AudioTrack',
        ),
        migrations.AddField(
            model_name='videoplaylist',
            name='video',
            field=models.ManyToManyField(through='uploads.VideoPlaylistLink', to='uploads.Video'),
        ),
        migrations.AddField(
            model_name='audioplaylist',
            name='audio',
            field=models.ManyToManyField(through='uploads.AudioPlaylistLink', to='uploads.Audio'),
        ),
    ]