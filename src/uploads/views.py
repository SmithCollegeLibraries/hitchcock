from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.list import ListView
from .models import Video, Audio, VideoPlaylist, AudioPlaylist, Text, Upload, SiteSetting
import uuid
from .panopto import panopto_oauth2
from html_sanitizer import Sanitizer
html_sanitizer = Sanitizer()
html = html_sanitizer.sanitize

def shib_bounce(request):
    """This view is for bouncing the user to the desired location after they
    have authenticated with Shibboleth and been bounced back to /login.
    Assumes that a 'next' argument has been set in the URL. E.g.
    '/login?next=/inventory/'.

    PersistentRemoteUserMiddleware logs the user in automatically, so there is
    no need for this view to do this work manually.
    """
    try:
        next = request.GET['next']
    except KeyError:
        raise Http404("No bounce destination.")
    if request.user.is_authenticated:
        return redirect(next)
    else:
        return HttpResponse("Error: Shibboleth authentication failed.")

@staff_member_required
def renew_panopto_token(request):
    oauth2 = panopto_oauth2.PanoptoOAuth2(
        settings.PANOPTO_SERVER,
        settings.PANOPTO_CLIENT_ID,
        settings.PANOPTO_CLIENT_SECRET,
        True,
        settings.PANOPTO_AUTH_CACHE_FILE_PATH,
    )
    # result = oauth2.get_new_token()
    result = oauth2.get_authorization_url()
    oauth_state = {
        'access_token_endpoint': oauth2.access_token_endpoint,
        'authorization_endpoint': oauth2.authorization_endpoint,
        'cache_file': oauth2.cache_file,
        'client_id': oauth2.client_id,
        'client_secret': oauth2.client_secret,
        'ssl_verify': oauth2.ssl_verify,
    }
    request.session['oath_state'] = oauth_state
    return redirect(result)

@staff_member_required
def panopto_oauth2_redirect(request):
    oauth2 = panopto_oauth2.PanoptoOAuth2(
        settings.PANOPTO_SERVER,
        settings.PANOPTO_CLIENT_ID,
        settings.PANOPTO_CLIENT_SECRET,
        True,
        settings.PANOPTO_AUTH_CACHE_FILE_PATH)
    token = oauth2.get_redirected_path(request.get_full_path())
    if token is not None:
        return HttpResponse("<p>Authorization complete! <pre>%s</pre></p> <p>New refresh token saved to <pre>%s</pre></p>" % (token, settings.PANOPTO_AUTH_CACHE_FILE_PATH))
    else:
        return HttpResponse("Authorization failed! No token found.")

def get_site_setting(setting_key):
    try:
        obj = SiteSetting.objects.get(setting_key__exact=setting_key)
        return obj.setting_value
    except SiteSetting.DoesNotExist:
        return None

class FacultyListInventory(LoginRequiredMixin, ListView):
    model = Upload
    paginate_by = 30
    template_name = "uploads/faculty_inventory_list.html"

    def get_queryset(self):
        object_list = self.model.objects.all().order_by('title')
        try:
            self.query = self.request.GET['q']
            object_list = object_list.filter(title__icontains = self.query)
            return object_list
        except KeyError:
            self.query = None
            return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title_text = get_site_setting('faculty_inventory_page_title')
        if title_text is not None:
            context['title'] = html(title_text)
        else:
            context['title'] = ''
        top_text = get_site_setting('faculty_inventory_text_block')
        if top_text is not None:
            context['top_text_content'] = html(top_text)
        else:
            context['top_text_content'] = ''

        context['query'] = self.query
        return context

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
        panopto_session_id = obj.panopto_session_id
        if panopto_session_id is not None:
            panopto_url = 'https://' + settings.PANOPTO_SERVER + '/Panopto/Pages/Viewer.aspx?id=' + panopto_session_id
        else:
            raise Http404("No video found")

        return redirect(panopto_url)
        # context = {
        #     'panopto_session_id': obj.panopto_session_id,
        # }
        # return render(request, 'uploads/video-panopto-embed.html', context)
    return render_video(request, obj)

def play_audio(request, pk):
    try:
        obj = get_object_or_404(Audio, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_audio(request, obj):
        panopto_session_id = obj.panopto_session_id
        if panopto_session_id is not None:
            panopto_url = 'https://' + settings.PANOPTO_SERVER + '/Panopto/Pages/Viewer.aspx?id=' + panopto_session_id
        else:
            raise Http404("No audio found")

        return redirect(panopto_url)
    return render_audio(request, obj)

def play_video_playlist(request, pk):
    try:
        obj = get_object_or_404(VideoPlaylist, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_video_playlist(request, obj):
        panopto_playlist_id = obj.panopto_playlist_id
        if panopto_playlist_id is not None:
            panopto_url = 'https://' + settings.PANOPTO_SERVER + '/Panopto/Pages/Viewer.aspx?pid=' + panopto_playlist_id
        else:
            raise Http404("Playlist not found")
        return redirect(panopto_url)
    return render_video_playlist(request, obj)

def play_audio_playlist(request, pk):
    try:
        obj = get_object_or_404(AudioPlaylist, pk=pk)
    except ValidationError:
        # Not a proper UUID, give a 404 in this case
        raise Http404("Invalid identifier")

    @staff_view_unpublished
    def render_audio_playlist(request, obj):
        panopto_playlist_id = obj.panopto_playlist_id
        if panopto_playlist_id is not None:
            panopto_url = 'https://' + settings.PANOPTO_SERVER + '/Panopto/Pages/Viewer.aspx?pid=' + panopto_playlist_id
        else:
            raise Http404("Playlist not found")
        return redirect(panopto_url)
    render_audio_playlist(request, obj)
