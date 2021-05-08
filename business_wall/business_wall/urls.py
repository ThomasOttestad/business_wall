"""business_wall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from notes import views
from inbox import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from homepage import views


urlpatterns = [
    path('', include('homepage.urls')),
    # path('', TemplateView.as_view(template_name='home.html')),
    # path('', TemplateView.as_view(template_name='codehome.html'), name='codehome'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')), #gir oss flere authentication views!
    path('notes/', include('notes.urls')),
    path('inbox/', include('inbox.urls')),
    path('timesheet/', include('timesheet.urls')),
    path('messageboards/', include('messageboard.urls')),
    path('profile/', include('userprofile.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('schema/',include('schema.urls')),
    path('roster/', include('roster.urls.pages')),
    path('api/', include('roster.urls.api')),
    path('departments/', include('departments.urls')),
    path('colleagues/', include('colleagues.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
