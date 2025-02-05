from . import views
from .models import Upload
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('texts/<str:pk>', views.show_text),
    path('videos/<str:pk>', views.play_video),
    path('audio/<str:pk>', views.play_audio),
    path('video-playlists/<str:pk>', views.play_video_playlist),
    path('audio-playlists/<str:pk>', views.play_audio_playlist),
    path('renew-panopto-token', views.renew_panopto_token),
    path('panopto-auth2-redirect', views.panopto_oauth2_redirect),
    path('inventory/', views.FacultyListInventory.as_view()),
    path('login/', views.shib_bounce),
]

# Serializers define the API representation.
class UploadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Upload
        fields = [
            'id',
            'url',
            'identifier',
            'title',
            'item_record_url',
            'barcode',
            'form',
            'description',
            'notes',
            'modified',
            'created',
            'size',
            'published',
            'link',
        ]

    # Define the link field to be the @url property of the model
    link = serializers.ReadOnlyField(source='url')

# ViewSets define the view behavior.
class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all().order_by('title')
    serializer_class = UploadSerializer

    def get_queryset(self):
        queryset = Upload.objects.all().order_by('title')
        title = self.request.query_params.get('title')
        if title is not None:
            queryset = queryset.filter(title__contains=title)
        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'uploads', UploadViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', obtain_auth_token, name='auth'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
