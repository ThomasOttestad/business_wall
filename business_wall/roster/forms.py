from django import forms
from .models import Shift, ShiftTrade
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q, F, ExpressionWrapper
from django.db import models
from datetime import timedelta
from dateutil.parser import parse
from util.functions import timedelta_to_hhmm
from datetime import datetime
from django.utils.timezone import make_aware

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()

class ShiftDurationField(forms.CharField):
    def clean(self, value):
        if not value:
            return
        try:
            date = parse(value)
        except ValueError as e:
            raise ValidationError("Enter a valid duration.")
        except Exception as e:
            raise ValidationError(str(e))
        else:
            return timedelta(hours=date.hour, minutes=date.minute)

class ShiftForm(forms.ModelForm):
    worker = UserModelChoiceField(queryset=User.objects.filter(groups__name__in=["worker"]).distinct())
    shift_leader = UserModelChoiceField(queryset=User.objects.filter(groups__name__in=["shift_leader","supervisor"]).distinct())
    duration = ShiftDurationField(initial=timedelta_to_hhmm(Shift._meta.get_field('duration').get_default()))

    class Meta:
        model = Shift
        fields = "__all__"

    def clean(self):
        super().clean()
        try:
            start = self.cleaned_data["start"]
            duration = self.cleaned_data["duration"]
            duration = duration if duration else Shift._meta.get_field('duration').get_default()
            end_time = start + duration
            worker = self.cleaned_data["worker"]
        except KeyError:
            pass
        else:
            prev = Shift.objects.annotate(
                end_time=ExpressionWrapper(F("start")+F("duration"),
                output_field=models.DateTimeField())
            ).filter(
                ~Q(pk=self.instance.pk),
                Q(start__range=(start,end_time)) |
                Q(end_time__range=(start,end_time)) |
                Q(start__lt=start, end_time__gt=start) |
                Q(start__lt=end_time, end_time__gt=end_time),
                worker=worker
            )
            if len(prev):
                raise ValidationError({"start": "Overlapping shifts."})

class ShiftTradeForm(forms.ModelForm):
    shift = forms.ModelChoiceField(queryset=Shift.objects.all(), widget=forms.Select(attrs={"hidden": True}))
    trader = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={"hidden": True}))

    class Meta:
        model = ShiftTrade
        fields = ["shift", "trader", "recipient", "supervisor"]

    def __init__(self, *args, **kwargs):
        init = True
        try:
            shift = kwargs.pop("shift")
            department = shift.department
            trader = kwargs.pop("trader")
        except KeyError:
            init = False
            shift = args[0]["shift"]
            department = shift.department
            trader = args[0]["trader"]

        super(ShiftTradeForm, self).__init__(*args, **kwargs)

        if init:
            self.fields["shift"].initial = shift
            self.fields["trader"].initial = trader

        self.fields["recipient"] = UserModelChoiceField(queryset = User.objects.filter(
                pk__in=[u.pk for u in department.users.all()]
        ).exclude(pk=trader.pk))

        self.fields["supervisor"] = UserModelChoiceField(queryset = User.objects.filter(
                Q(groups__name="supervisor") &
                Q(pk__in=[u.pk for u in department.users.all()])
        ))

    def clean(self):
        super().clean()
        try:
            trader = self.cleaned_data["trader"]
            recipient = self.cleaned_data["recipient"]
            shift = self.cleaned_data["shift"]
        except KeyError:
            pass
        else:
            trades = ShiftTrade.objects.filter(Q(shift=shift) & (Q(recipient_answer=None) | Q(supervisor_answer=None)))
            if trades:
                raise ValidationError("A request for this shift already exists.")

            if trader == recipient:
                raise ValidationError({"recipient": "You cannot trade a shift with yourself."})

            diff = shift.start - make_aware(datetime.today())
            if diff < timedelta(hours=24):
                raise ValidationError("You can only request a shift trade 24 hours before it starts.")


class ShiftTradeAnswerForm(forms.Form):
    answer = forms.IntegerField()

    def __init__(self, trade, user, *args, **kwargs):
        super(ShiftTradeAnswerForm, self).__init__(*args, **kwargs)
        self.user = user
        self.trade = trade

    def clean(self):
        super().clean()
        diff = self.trade.shift.start - make_aware(datetime.today())
        if diff < timedelta(hours=24):
            raise ValidationError("You can only answer the request 24 hours before the shift starts.")

    def save(self):
        self.trade.answer(self.user, self.cleaned_data["answer"])
