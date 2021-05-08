from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'schema'

urlpatterns = [
    
    # url(r'^$' views.schema_home),
    path('list', views.list_schema, name='list'),
    path('create',views.create_schema, name='create'),
    path('',views.schema_home, name='home'),
]

