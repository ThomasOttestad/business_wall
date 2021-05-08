from django import forms
from .models import Department
from messageboard.models import Board
from django.core.exceptions import ValidationError
from roster.forms import ShiftForm
from django.contrib.auth.models import User
from django.db.models import Q

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()

class UserMultipleModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()

class DepartmentForm(forms.ModelForm):
    manager = UserModelChoiceField(queryset=User.objects.filter(groups__name__in=["supervisor"]))
    users = UserMultipleModelChoiceField(queryset=User.objects.all(), help_text="Hold down “Control”, or “Command” on a Mac, to select more than one.")
    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            b = Board.objects.get(name=name)
        except Exception as e:
            return name
        raise ValidationError(f"A messageboard called '{name}' already exists.")


    class Meta:
        model = Department
        fields = ["name", "manager", "users"]

class DepartmentUpdateForm(forms.ModelForm):
    manager = UserModelChoiceField(queryset=User.objects.filter(groups__name__in=["supervisor"]))
    class Meta:
        model = Department
        fields = ["name", "manager"]

class AddUserDepartmentForm(forms.Form):
    def __init__(self, department, *args, **kwargs):
        super(AddUserDepartmentForm, self).__init__(*args, **kwargs)
        self.fields["users"] = forms.ModelMultipleChoiceField(
                queryset=User.objects.all().exclude(pk__in=[u.pk for u in department.users.all()]),
                help_text="Hold down “Control”, or “Command” on a Mac, to select more than one."
        )
