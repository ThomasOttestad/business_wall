from django.urls import path
# from departments.views import DepartmentsView, DepartmentHomeView, NewDepartmentView, DeleteDepartmentView, UpdateDepartmentView, AddUserDepartmentView
from departments.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(DepartmentsView.as_view()), name="departments"),
    path('<int:did>', login_required(DepartmentHomeView.as_view()), name="department_home"),
    path('new', login_required(NewDepartmentView.as_view()), name="new_department"),
    path('<int:pk>/delete', login_required(DeleteDepartmentView.as_view()), name="delete_department"),
    path('<int:pk>/update', login_required(UpdateDepartmentView.as_view()), name="update_department"),
    path('<int:pk>/users/add', login_required(AddUserDepartmentView.as_view()), name="add_user_department"),
    path('<int:pk>/users/<int:uid>/remove', login_required(RemoveUserDepartmentView.as_view()), name="remove_user_department"),
]
