from django.db import models
from django.contrib.auth.models import User
from messageboard.models import Board
from django.db.models import Q


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="manager")
    users = models.ManyToManyField(User, blank=True, related_name="users")
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/departments/{self.id}"

    def get_members(self, query=None):
        if query:
            return self.users.filter(
                Q(first_name__contains=query) |
                Q(last_name__contains=query)  | 
                Q(username__contains=query)
            )
        return self.users.all()
