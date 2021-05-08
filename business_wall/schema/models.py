from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Schema(models.Model):
    schema_id = models.AutoField(primary_key=True)
    issue = models.CharField(max_length=100)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default=None)

    def __str__(self):
        return self.issue
        
