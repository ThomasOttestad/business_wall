from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime, time
import holidays

class Time(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=None, null=True)
    time_worked = models.DurationField(default=timedelta(minutes=0))
    overtime = models.DurationField(default=timedelta(minutes=0))
    evening = models.DurationField(default=timedelta(minutes=0))
    weekend = models.DurationField(default=timedelta(minutes=0))
    holiday = models.DurationField(default=timedelta(minutes=0))
    note = models.TextField(default='', blank=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.start_time, self.end_time, self.note)
    
    
    def check_additional(self, overtime, end_of_day):
        self.time_worked = self.end_time - self.start_time
        get_endtime = self.end_time.time()
        get_date = self.start_time.date()
        get_day = get_date.isoweekday()
        get_holidays = holidays.Norway(include_sundays=False)

        if self.time_worked > overtime:
            self.overtime = self.time_worked - overtime

        if get_endtime > end_of_day:
            if self.start_time.time() >= end_of_day:
                self.evening = self.time_worked

            else:
                self.evening = self.end_time - timezone.make_aware(datetime.combine(get_date, end_of_day))
        
        if get_day == 6 or get_day == 7:
            self.weekend = self.time_worked
        
        if get_date in get_holidays:
            self.holiday = self.time_worked

    def find_sum(self):

        if self.holiday:
            return self.time_worked - self.holiday
        
        if self.weekend:
            return self.time_worked - self.weekend

        if self.overtime or self.evening:
            if self.overtime > self.evening:
                return self.time_worked - self.overtime
            
            else:
                return self.time_worked - self.evening
        
        return self.time_worked


class AdditionalRate(models.Model):
    normal_rate = models.IntegerField(default=0) 
    overtime_rate = models.IntegerField(default=50)
    holiday_rate = models.IntegerField(default=100)
    weekend_rate = models.IntegerField(default=25)
    evening_rate = models.IntegerField(default=15)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.overtime_rate, self.holiday_rate, self.weekend_rate, self.evening_rate)
    

class Stamp(models.Model): 
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    stampedIn = models.BooleanField(default=False)
    time_model = models.ManyToManyField(Time, blank=True)
    additonal_rate = models.ForeignKey(AdditionalRate, on_delete=models.CASCADE, null=True)
    end_of_day = models.TimeField(default=time(hour=16))
    shift_duration = models.DurationField(default=timedelta(hours=8))

    def __str__(self):
        return str(self.worker)

    def set_end_time(self):
        stamp_out_time = self.time_model.get(end_time = None)
        stamp_out_time.end_time = timezone.now()
        stamp_out_time.save()

class PayCheck(models.Model):
    taxes = models.IntegerField(default=25)
    vacation_money_basis = models.FloatField(default=12)
    worker = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    wage = models.FloatField(default=0)


    def set_wage(self, money_earned):
        self.wage = round((1 - (self.taxes / 100)) * money_earned, 2)