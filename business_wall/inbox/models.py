from django.db import models
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import truncatechars

class Message(models.Model):
    """
    Messages between users
    """
    sender = models.ForeignKey(User, null=True, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    multiple_receivers = models.CharField(max_length=255, blank=True)
    msg_title = models.CharField(max_length=56)
    msg_content = models.TextField(blank=True)
    sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def getLastMsg(self):
        return Message.objects.order_by('-sent').first()
    
    def get_short_title(self):
        return truncatechars(self.msg_title, 10)
        