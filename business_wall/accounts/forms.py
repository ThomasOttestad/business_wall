from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
import uuid
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .util import create_user
from .models import SignupToken
from django.template.loader import render_to_string


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean(self):
        super().clean()
        try:
            email = self.cleaned_data["email"]
            User.objects.get(email=email)
        except User.DoesNotExist:
            return
        else:
            raise ValidationError({"email": "Email already exists"})

    def save(self):
        create_user(
            ["worker"],
            username=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password1')
        )

class EmployeeInviteForm(forms.ModelForm):
    email = forms.EmailField(help_text="Specify the email to send an invite link")

    class Meta:
        model = SignupToken
        fields = []


    def save(self):
        token = SignupToken.objects.create()

        msg_plain = render_to_string('mail/token.txt', {
            "company": settings.COMPANY_NAME,
            "url": settings.SITE_URL + "/accounts/signup/?token=" + str(token.token),
            "email": self.cleaned_data["email"]
        })

        send_mail(
            f"{settings.COMPANY_NAME} account registration",
            msg_plain,
            settings.EMAIL_NO_REPLY,
            [self.cleaned_data["email"]],
            fail_silently=False,
        )


class EmployeeRegistrationForm(forms.ModelForm):
    position = forms.ModelChoiceField(queryset=Group.objects.all())

    class Meta(object):
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean(self):
        super().clean()
        try:
            email = self.cleaned_data["email"]
            User.objects.get(email=email)
        except User.DoesNotExist:
            return
        else:
            raise ValidationError({"email": "Email already exists"})

    def save(self):
        position = self.cleaned_data.pop("position")
        password = get_random_string(16)

        employee = create_user(
            [position.name],
            username=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=password
        )

        msg_plain = render_to_string('mail/registered_empoyee.txt', {
            "company": settings.COMPANY_NAME,
            "url": settings.SITE_URL,
            "email": employee.email,
            "password": password
        })

        send_mail(
            f"{settings.COMPANY_NAME} account registration",
            msg_plain,
            settings.EMAIL_NO_REPLY,
            [employee.email],
            fail_silently=False,
        )
