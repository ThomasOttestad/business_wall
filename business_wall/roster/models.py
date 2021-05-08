from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from util.functions import timedelta_to_hhmm
from departments.models import Department
import moment
from django.conf import settings

colors = [
    "rgba(230, 25, 75,0.3)",
    "rgba(60, 180, 75,0.3)",
    "rgba(255, 225, 25,0.3)",
    "rgba(0, 130, 200,0.3)",
    "rgba(245, 130, 48,0.3)",
    "rgba(145, 30, 180,0.3)",
    "rgba(70, 240, 240,0.3)",
    "rgba(240, 50, 230,0.3)",
    "rgba(210, 245, 60,0.3)",
    "rgba(250, 190, 190,0.3)",
    "rgba(0, 128, 128,0.3)",
    "rgba(230, 190, 255,0.3)",
    "rgba(170, 110, 40,0.3)",
    "rgba(255, 250, 200,0.3)",
    "rgba(128, 0, 0,0.3)",
    "rgba(170, 255, 195,0.3)",
    "rgba(128, 128, 0,0.3)",
    "rgba(255, 215, 180,0.3)",
    "rgba(0, 0, 128,0.3)",
    "rgba(128, 128, 128,0.3)",
    "rgba(255, 255, 255,0.3)",
]

class Shift(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, default=None)
    worker = models.ForeignKey(User, related_name="worker", on_delete=models.CASCADE)
    shift_leader = models.ForeignKey(User, related_name="shift_leader", null=True, on_delete=models.SET_NULL)

    start = models.DateTimeField()
    duration =  models.DurationField(default=timedelta(hours=8))

    def __str__(self):
        return str(self.worker) + ": " + self.duration_str()

    def duration_str(self):
        start = moment.date(self.start).locale(settings.TIME_ZONE).format("ddd DD/MM/YYYY HH:mm")
        if self.start.month == self.end.month and self.start.day == self.end.day:
            end = moment.date(self.end).locale(settings.TIME_ZONE).format("HH:mm")
        else:
            end = moment.date(self.end).locale(settings.TIME_ZONE).format("ddd DD/MM/YYYY HH:mm")
        return f"{start}-{end}"

    @property
    def end(self):
        return self.start + self.duration

    def get_absolute_url(self):
        return "/shift/%i/" % self.id

    def generate_event(self):
        return {
            "id": str(self.id),
            "worker": self.worker.id,
            "title": self.worker.get_full_name(),
            "start": str(self.start),
            "end": str(self.start+self.duration),
            "organizer": self.shift_leader.get_full_name(),
            "location": str(self.department.name),
            "color": colors[self.worker.id % len(colors)]
        }

class ShiftTrade(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    trader = models.ForeignKey(User, related_name="trader", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="recipient", on_delete=models.CASCADE)
    recipient_answer = models.BooleanField(default=None, null=True)
    supervisor = models.ForeignKey(User, related_name="supervisor", on_delete=models.CASCADE)
    supervisor_answer = models.BooleanField(default=None, null=True)

    def __str__(self):
        return f"{self.trader} -> {self.recipient} ({self.shift})"

    def state(self):
        evaluating = self.evaluating()
        if evaluating == None:
            return f"The shift trade has been {'accepted' if self.accepted() else 'declined'}."
        else:
            return f"The shift is being evaluated by {evaluating}."

    def accepted(self):
        return self.recipient_answer and self.supervisor_answer

    def evaluating(self):
        if self.recipient_answer == None:
            return self.recipient
        elif self.supervisor_answer == None:
            return self.supervisor
        return None

    def answer(self, user, answer):
        prev = self.accepted()
        if user == self.recipient:
            self.recipient_answer = answer
        elif user == self.supervisor:
            self.supervisor_answer = answer
        else:
            raise Exception("Invalid user")
        self.save()

        if prev != self.accepted():
            if self.accepted():
                self.shift.worker = self.recipient
            else:
                self.shift.worker = self.trader
            self.shift.save()

    def revert(self):
        self.shift.worker = self.trader
        self.shift.save()

        self.delete()
