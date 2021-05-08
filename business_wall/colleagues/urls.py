from django.urls import path
from colleagues.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(ColleaguesView.as_view()), name="colleagues"),
]
