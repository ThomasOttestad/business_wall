from django import forms
import calendar
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


MONTHS = tuple(zip(range(1,13), (calendar.month_name[i] for i in range(1,13))))
YEARS = tuple(zip(range(2020,2022), range(2020,2022)))

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()

class CalenderPickerForm(forms.Form):
    worker = UserModelChoiceField(queryset=User.objects.filter(groups__name__in=['worker']).distinct(), required=False)
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.ChoiceField(choices=YEARS)

class NoteForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ['note']

class TimeForm(forms.ModelForm):
    start_time = forms.DateTimeField(required=False)
    end_time = forms.DateTimeField(required=False)

    def clean(self):
        super().clean()
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time and end_time and end_time < start_time:
            raise ValidationError({"end_time":"End time has to come after start time"})

    class Meta:
        model = Time
        fields = ['start_time', 'end_time', 'note']
