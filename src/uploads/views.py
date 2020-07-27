from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Video, Audio

def play_video(request, pk):
    obj = get_object_or_404(Video, pk=pk)
    path_from_av = obj.upload.name.replace(settings.AV_SUBDIR_NAME, '')
    wowza_url_hls = settings.WOWZA_ENDPOINT + 'mp4:' + path_from_av + '/playlist.m3u8'
    context = {
        'wowza_url_hls': wowza_url_hls,
    }
    return render(request, 'uploads/video-player-theo.html', context)
