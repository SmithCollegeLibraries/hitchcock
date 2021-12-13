from . import views
from django.urls import path

urlpatterns = [
    path('texts/<str:pk>', views.show_text),
    path('videos/<str:pk>', views.play_video),
    path('audio/<str:pk>', views.play_audio),
    path('video-playlists/<str:pk>', views.play_video_playlist),
    path('audio-playlists/<str:pk>', views.play_audio_playlist),
    path('admin/renew-panopto-token', views.renew_panopto_token),
    path('panopto-auth2-redirect', views.panopto_oauth2_redirect),
    path('inventory/', views.FacultyListInventory.as_view()),
    path('login/', views.shib_bounce),
]
