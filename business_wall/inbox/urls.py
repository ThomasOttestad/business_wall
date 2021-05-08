from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.inbox), name='inbox'),
    path('send_message/', login_required(views.send_message), name='send_message'),
    path('delete_message/<int:id>', views.delete_message, name='delete_message'),
    path('populate_inbox/', views.populate_inbox, name='populate_inbox'),
    path('undelete_message/<int:id>', views.undelete_message, name='undelete_message'),
]