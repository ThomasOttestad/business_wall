from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
   path('', login_required(views.index), name="notes"),
   path('edit/<int:id>', views.edit, name='edit'),
   path('add/', views.add, name='add'), 
]