import datetime
from django import template
from django.utils.timesince import timesince

register = template.Library()
# Timedelta only has days and seconds, double // is for floor calculating
@register.filter()
def duration_format(td):
    tot_sec = td.seconds
    hours = tot_sec //3600
    minutes = ((tot_sec // 60)%60)//6
    if minutes == 0:
        return "{}".format(hours)
    return "{},{}".format(hours, minutes)
    
@register.filter()
def convert_hours(td):
    tot_sec = td.seconds
    tot_days = td.days
    hours = (tot_days * 24) + (tot_sec // 3600)
    minutes = ((tot_sec // 60)%60)//6
    if minutes == 0:
        return "{}".format(hours)
    return "{},{}".format(hours, minutes)