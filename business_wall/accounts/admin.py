from django.contrib import admin
from .models import SignupToken, UserProxy

admin.site.register(SignupToken)
admin.site.register(UserProxy)
