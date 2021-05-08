from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

def user_directory_path_pic(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/username/<filename>
    filename = 'profile'
    return 'images/{}'.format(filename)

def user_directory_path_doc(instance, filename):
    # file will be uploaded to MEDIA_ROOT/documents/username/<filename>
    return 'documents/{}/{}'.format(User.username, filename)

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Avatar(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Avatar_Main_Img = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Contract(models.Model):
    wage = models.FloatField(default=200.0)
    worker = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
