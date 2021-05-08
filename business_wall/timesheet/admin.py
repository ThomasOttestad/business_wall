from django.contrib import admin
from . import models

admin.site.register(models.Stamp)
admin.site.register(models.Time)
admin.site.register(models.AdditionalRate)
admin.site.register(models.PayCheck)