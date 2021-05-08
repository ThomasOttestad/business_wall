from django.shortcuts import render
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic.edit import FormView, DeleteView, UpdateView
from .models import Department
from .forms import DepartmentForm, DepartmentUpdateForm, AddUserDepartmentForm
from django.contrib.auth.models import User
from .util import create_department
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404


class DepartmentsView(View):
    def get(self, request, *args, **kwargs):

        page = int(request.GET.get("p", 1))
        psize = int(request.GET.get("pSize", 10))
        query = request.GET.get("q", None)

        if query:
            departments = Department.objects.filter(name__contains=query)
        else:
            departments = Department.objects.all()

        paginator = Paginator(departments, psize)
        try:
            currentPage = paginator.page(page)
        except EmptyPage:
            raise Http404

        context = {
            "departments": currentPage,
            "paginator": paginator,
            "query": query if query else ""
        }

        return render(request, "departments.html", context)

class DepartmentHomeView(View):
    def get(self, request, did, *args, **kwargs):
        department = get_object_or_404(Department, pk=did)
        if not request.user.groups.filter(name__in=["supervisor"]):
            return render(request, "401.html", status=401)

        page = int(request.GET.get("p", 1))
        psize = int(request.GET.get("pSize", 10))
        query = request.GET.get("q", None)

        paginator = Paginator(department.get_members(query), psize)
        try:
            currentPage = paginator.page(page)
        except EmptyPage:
            raise Http404

        context = {
            "department": department,
            "members": currentPage,
            "paginator": paginator,
            "query": query if query else ""
        }

        return render(request, "department/home.html", context)

class NewDepartmentView(FormView):
    template_name = "department/new.html"
    form_class = DepartmentForm
    success_url = "/departments"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.add_department"):
            return render(request, "401.html", status=401)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.add_department"):
            return render(request, "401.html", status=401)
        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        dep = create_department(**form.cleaned_data)
        # dep = create_department(users=[form.cleaned_data.get("manager")], **form.cleaned_data)
        if dep:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

class DeleteDepartmentView(DeleteView):
    template_name = "department/delete.html"
    success_url = "/departments"
    model = Department

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.delete_department"):
            return render(request, "401.html", status=401)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.delete_department"):
            return render(request, "401.html", status=401)
        return super().post(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.board.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

class UpdateDepartmentView(UpdateView):
    model = Department
    form_class = DepartmentUpdateForm
    # fields = ["name", "manager"]
    template_name = "department/update.html"
    success_url = "/departments"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        dep = self.get_object()
        b = dep.board
        name = form.cleaned_data.get("name")
        b.name = name
        b.description = f"Messageboard for {name} department."
        b.save()
        form.save()
        return super().form_valid(form)

class AddUserDepartmentView(FormView):
    template_name = "department/users/add.html"
    form_class = AddUserDepartmentForm
    success_url = "/departments"

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.department, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({"object": self.department})
        return kwargs

    def get(self, request, pk, *args, **kwargs):
        self.department = get_object_or_404(Department, pk=pk)
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, pk, *args, **kwargs):
        self.department = get_object_or_404(Department, pk=pk)
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        users = form.cleaned_data.get("users")
        self.department.users.add(*users)
        self.department.save()
        return super().form_valid(form)

class RemoveUserDepartmentView(DeleteView):
    template_name = "department/users/remove.html"
    success_url = "/departments"
    model = Department

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({"user": self.user})
        return kwargs

    def get(self, request, uid, *args, **kwargs):
        department = get_object_or_404(Department, pk=kwargs.get("pk"))
        self.user = get_object_or_404(User, Q(pk=uid) & Q(pk__in=[u.pk for u in department.users.all()]))
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, uid, *args, **kwargs):
        department = get_object_or_404(Department, pk=kwargs.get("pk"))
        self.user = get_object_or_404(User, Q(pk=uid) & Q(pk__in=[u.pk for u in department.users.all()]))
        if not request.user.has_perm("departments.change_department"):
            return render(request, "401.html", status=401)
        return super().post(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.users.remove(self.user)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
