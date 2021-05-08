from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group, User
from .forms import SignUpForm, EmployeeRegistrationForm, EmployeeInviteForm
from .models import SignupToken
from timesheet.models import Stamp, AdditionalRate
from .util import create_user
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView, FormView
import os



class SignupView(View):
    def verify_token(self):
        try:
            token = self.request.GET.get("token")
            return bool(SignupToken.valid.get(token=token))
        except Exception as e:
            return False

    def get(self, request, *args, **kwargs):
        context = {
            "form": SignUpForm(),
            "tokens": settings.SIGNUP_TOKENS,
            "validtoken": self.verify_token()
        }

        return render(request, 'signup.html', context)


    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        validtoken = self.verify_token()

        if (validtoken or not settings.SIGNUP_TOKENS) and form.is_valid():
            form.save()

            if validtoken:
                SignupToken.objects.get(token=self.request.GET.get("token")).delete()
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))

            login(request, user)
            return redirect('home')

        context = {
            "form": form,
            "tokens": settings.SIGNUP_TOKENS,
            "validtoken": validtoken
        }
        return render(request, 'signup.html', context)


class EmployeeRegistrationView(FormView):
    template_name = "register_employee.html"
    form_class = [EmployeeRegistrationForm, EmployeeInviteForm]
    success_url = "/colleagues"

    def get_form_class(self):
        if not settings.SIGNUP_TOKENS:
            return self.form_class[1]
        return self.form_class[0]

    def get(self, request, *args, **kwargs):
        if not request.user.is_manager():
            raise PermissionDenied
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_manager():
            raise PermissionDenied
        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
