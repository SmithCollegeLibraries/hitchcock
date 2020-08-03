from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Video, Audio, AudioAlbum

def play_video(request, pk):
    obj = get_object_or_404(Video, pk=pk)
    path_from_av = obj.upload.name.replace(settings.AV_SUBDIR_NAME, '')
    wowza_url_hls = settings.WOWZA_ENDPOINT + 'mp4:' + path_from_av + '/playlist.m3u8'
    context = {
        'wowza_url_hls': wowza_url_hls,
    }
    return render(request, 'uploads/video-player-theo.html', context)

def play_audio(request, pk):
    obj = get_object_or_404(Audio, pk=pk)
    path_from_av = obj.upload.name.replace(settings.AV_SUBDIR_NAME, '')
    wowza_url_hls = settings.WOWZA_ENDPOINT + 'mp3:' + path_from_av + '/playlist.m3u8'
    context = {
        'wowza_url_hls': wowza_url_hls,
    }
    return render(request, 'uploads/video-player-theo.html', context)

def play_audio_album(request, pk):
    obj = get_object_or_404(AudioAlbum, pk=pk)
    wowza_urls_hls = []
    for track in obj.audiotrack_set.all():
        path_from_av = track.upload.name.replace(settings.AV_SUBDIR_NAME, '')
        myurl = settings.WOWZA_ENDPOINT + 'mp3:' + path_from_av + '/playlist.m3u8'
        track_info = {
            "url": myurl,
            "title": track.title
        }
        wowza_urls_hls.append(track_info)
    wowza_url_hls = wowza_urls_hls[0]
    context = {
        'title': obj.title,
        'wowza_urls_hls': wowza_urls_hls,
    }
    return render(request, 'uploads/audio-album-player-theo.html', context)
