from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [
    path('userprofile/', views.index, name='userprofile'),
    path('userprofile/upload', views.upload, name='upload'),
    path('userprofile/documents', views.documents, name='documents'),
    path('userprofile/change', views.change, name='change'),
]
