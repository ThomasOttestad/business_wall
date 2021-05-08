from django.urls import path
from .views import SignupView, EmployeeRegistrationView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('register_employee/', EmployeeRegistrationView.as_view(), name='register_employee'),
]
