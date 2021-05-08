from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class Note(models.Model):
    note = models.CharField(max_length=400, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.note