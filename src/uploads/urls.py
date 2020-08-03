from . import views
from django.urls import path

urlpatterns = [
    path('videos/<int:pk>', views.play_video),
    path('audio/<int:pk>', views.play_audio),
    path('audio-album/<int:pk>', views.play_audio_album)
]
