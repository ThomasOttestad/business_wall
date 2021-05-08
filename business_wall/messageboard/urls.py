from django.contrib import admin
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('board/', views.board_home, name='board_home'),
    path('board/new/', views.new_board, name='new_board'),
    path('board/pinned/', views.pinned, name='pinned_topics'),
    path('board/<int:pk>/', views.TopicListView.as_view(), name='board_topics'),
    path('board/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('board/<int:pk>/topics/<int:topic_pk>', views.PostListView.as_view(), name='topic_posts'),
    path('board/<int:pk>/topics/<int:topic_pk>/reply', views.reply_topic, name='reply_topic'),
    path('board/<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('delete/<int:post_pk>', views.delete_comfirm, name='delete'),
    path('delete/message/', views.delete, name='delete_post'),
]
