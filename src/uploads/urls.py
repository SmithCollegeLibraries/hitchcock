from . import views
from django.urls import path

urlpatterns = [
    path('videos/<str:pk>', views.play_video),
    path('audio/<str:pk>', views.play_audio),
    path('audio-album/<str:pk>', views.play_audio_album)
]
