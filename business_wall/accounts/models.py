from django.db import models
from django.contrib.auth.models import User as django_user
from roster.models import ShiftTrade
from departments.models import Department
from django.db.models import Q
from datetime import datetime, timedelta
import uuid
from django.db.models import Q, F, ExpressionWrapper
from django.utils.timezone import make_aware
from userprofile.models import Avatar
from django.templatetags.static import static


class UserProxy(django_user):
    class Meta:
        proxy = True

    def pending_trades(self):
        return ShiftTrade.objects.filter(Q(trader=self) & (Q(recipient_answer=None) | Q(supervisor_answer=None)))

    def accepted_trades(self):
        return ShiftTrade.objects.filter(trader=self, recipient_answer=True, supervisor_answer=True)

    def declined_trades(self):
        return ShiftTrade.objects.filter(Q(trader=self) & (Q(recipient_answer=False) | Q(supervisor_answer=False)))

    def requested_trades(self):
        return ShiftTrade.objects.filter(Q(recipient=self) & Q(recipient_answer=None) | Q(supervisor_answer=None))

    def get_departments(self):
        return Department.objects.filter(users=self)

    """The group with the most permissions is most likely the highest position"""
    def get_position(self):
        position = None
        for g in self.groups.all():
            if not position or position.permissions.all().count() < g.permissions.all().count():
                position = g
        return g

    def is_manager(self):
        try:
            self.groups.get(name="supervisor")
        except Exception as e:
            return False
        else:
            return True

    def get_avatar(self):
        try:
            avatar = Avatar.objects.get(user__pk=self.pk)
            url = avatar.Avatar_Main_Img.url
        except Exception as e:
            url = static("/images/avatar.png")
        return url


class ValidSignupTokenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter().annotate(
                expires_at=ExpressionWrapper(F("created_at")+F("valid_for"),
                output_field=models.DateTimeField())
            ).filter(expires_at__gt=make_aware(datetime.now()))

class InValidSignupTokenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter().annotate(
                expires_at=ExpressionWrapper(F("created_at")+F("valid_for"),
                output_field=models.DateTimeField())
            ).filter(expires_at__lt=make_aware(datetime.now()))

class SignupToken(models.Model):
    token = models.CharField(max_length=255, default=uuid.uuid4())
    created_at = models.DateTimeField(auto_now_add=True)
    valid_for = models.DurationField(default=timedelta(days=3))

    objects = models.Manager()
    valid = ValidSignupTokenManager()
    invalid = InValidSignupTokenManager()

    def __str__(self):
        return self.token
