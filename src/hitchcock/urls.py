"""hitchcock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.views.generic import RedirectView

# This is a hacky way to set text in the admin site, but it works...
# https://stackoverflow.com/questions/4938491/django-admin-change-header-django-administration-text
admin.sites.AdminSite.site_header = 'Hitchcock Smith Libraries e-reserves administration'
admin.sites.AdminSite.site_title = 'Hitchcock Smith Libraries e-reserves administration'
admin.sites.AdminSite.site_url = None # Disable "view site" link in header
admin.sites.AdminSite.enable_nav_sidebar = False

urlpatterns = [
    # Skip the uploads app index page and go directly to the changelist
    path('admin/uploads/', RedirectView.as_view(url=settings.BASE_URL + '/admin/uploads/upload/')),
    path('admin/', admin.site.urls),
    path('', include('uploads.urls')),
]
