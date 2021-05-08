from django.urls import path
from roster.views.api import ShiftFeed, ShiftFeedUser, ShiftFeedDepartment, ShiftEdit
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("shifts", login_required(ShiftFeed.as_view()), name="api_shifts"),
    path("shifts/user/<int:uid>", login_required(ShiftFeedUser.as_view()), name="api_shifts_user"),
    path("shifts/department/<int:did>", login_required(ShiftFeedDepartment.as_view()), name="api_shifts_department"),
    path("shifts/<int:sid>", login_required(ShiftEdit.as_view()), name="api_shift"),
]
