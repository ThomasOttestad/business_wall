from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.edit_timesheet), name='timesheet'),
    # path('edit_timesheet/', login_required(views.edit_timesheet), name='edit_timesheet'),
    path('stampin/', login_required(views.stamp_in), name='stampin'),
    path('stampout/', login_required(views.stamp_out), name='stampout'),
    path('edit_note/<int:id>', login_required(views.edit_note), name='edit'),
    path('edit_time/<int:id>', login_required(views.edit_time), name='edit_time'),
    path('paycheck/', login_required(views.generate_paycheck), name='paycheck'),
    path('estimate_paycheck/', login_required(views.estimate_paycheck), name='estimate_paycheck'),
    path('populate/', login_required(views.populate_database), name='populate'),
]
