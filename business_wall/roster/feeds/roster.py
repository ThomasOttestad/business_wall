from django_ical.views import ICalFeed
from roster.models import Shift
from departments.models import Department
from django.conf import settings
from django.contrib.auth.models import User

class RosterFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = '-//Business wall//Roster//EN'
    timezone = settings.TIME_ZONE
    file_name = "event.ics"

    def items(self):
        return Shift.objects.all().order_by('start')

    def item_title(self, item):
        return item.worker

    def item_start_datetime(self, item):
        return item.start

    def item_end_datetime(self, item):
        return item.start + item.duration

    def item_organizer(self, item):
        return item.shift_leader

    def item_location(self, item):
        return item.department.name

class RosterFeedDepartment(RosterFeed):

    def get_object(self, request, did):
        return Department.objects.get(pk=did)

    def items(self, department):
        return Shift.objects.filter(department=department).order_by('start')

class RosterFeedWorker(RosterFeed):

    def get_object(self, request, uid):
        return User.objects.get(pk=uid)

    def items(self, user):
        return Shift.objects.filter(worker=user).order_by('start')
