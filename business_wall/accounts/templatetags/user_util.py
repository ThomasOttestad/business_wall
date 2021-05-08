from django import template
from roster.models import ShiftTrade
from accounts.models import UserProxy
from userprofile.models import Avatar
from departments.models import Department
from django.templatetags.static import static

register = template.Library()

"""The group with the most permissions is most likely the highest position"""
@register.filter()
def get_position(user):
    position = None
    for g in user.groups.all():
        if not position or position.permissions.all().count() < g.permissions.all().count():
            position = g
    return position

@register.filter()
def get_avatar(user):
    try:
        avatar = Avatar.objects.get(user__pk=user.pk)
        url = avatar.Avatar_Main_Img.url
    except Exception as e:
        url = static("/images/avatar.png")
    return url

@register.filter()
def get_departments(user):
    return Department.objects.filter(users=user)
