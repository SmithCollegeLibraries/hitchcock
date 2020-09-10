from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required, permission_required
from .models import Video, Audio, AudioAlbum, Text, Upload
import uuid

@permission_required('uploads.view_inventory')
def faculty_view_inventory(request):
    context = {
        'uploads': Upload.objects.order_by('title'),
    }
    return render(request, 'uploads/faculty_view_inventory.html', context)

def staff_view_unpublished(render_func):
    """ Decorator for checking whether an item is unpublished.
    If unpublished, only allow staff to view the item.
    """
    def wrapper(request, obj):
        if obj.published is True:
            return render_func(request, obj)
        else:
            if request.user.is_staff is True:
                return render_func(request, obj)
            else:
                raise PermissionDenied
    return wrapper

def show_text(request, pk):
    try:
        obj = get_object_or_404(Text, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_text(request, obj):
        pdf_url = obj.stream_url
        return redirect(pdf_url)
    return render_text(request, obj)

def play_video(request, pk):
    try:
        obj = get_object_or_404(Video, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_video(request, obj):
        path_from_av = obj.upload.name.replace(settings.AV_SUBDIR_NAME, '')
        wowza_url_hls = settings.WOWZA_ENDPOINT + 'mp4:' + path_from_av + '/playlist.m3u8'

        _vtt_tracks = obj.videovtttrack_set.all()
        if len(_vtt_tracks) > 0:
            vtt_tracks = _vtt_tracks
        else:
            vtt_tracks = None

        context = {
            'wowza_url_hls': wowza_url_hls,
            'vtt_tracks': vtt_tracks,
        }
        return render(request, 'uploads/video-player-theo.html', context)
    return render_video(request, obj)

def play_audio(request, pk):
    try:
        obj = get_object_or_404(Audio, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_audio(request, obj):
        path_from_av = obj.upload.name.replace(settings.AV_SUBDIR_NAME, '')
        wowza_url_hls = settings.WOWZA_ENDPOINT + 'mp3:' + path_from_av + '/playlist.m3u8'
        context = {
            'wowza_url_hls': wowza_url_hls,
        }
        return render(request, 'uploads/video-player-theo.html', context)
    return render_audio(request, obj)

def play_audio_album(request, pk):
    try:
        obj = get_object_or_404(AudioAlbum, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_audio_album(request, obj):
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
    return render_audio_album(request, obj)
