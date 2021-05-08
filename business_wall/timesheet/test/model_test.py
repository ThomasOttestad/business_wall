from django.test import TestCase
from timesheet.models import Time, Stamp, AdditionalRate, PayCheck
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time


class StampModelTest(TestCase):
    def test_stamp_status(self):
        newstamp = Stamp()
        self.assertTrue(newstamp, False)

class TimeModelTest(TestCase):
    def test_time_end_time(self):
        start_time = timezone.make_aware(datetime(2020, 1, 1, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 1, 16))
        time = Time(start_time=start_time, end_time=end_time)
        if time.end_time <= time.start_time:
            raise ValidationError('End time cannot come before start time')

    def test_time_worked(self):
        start_time = timezone.make_aware(datetime(2020, 1, 1, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 1, 16))
        end_of_day = time(hour=16)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)
        time_worked = end_time - start_time

        self.assertEqual(timeModel.time_worked, time_worked)

    def test_time_overtime(self):
        start_time = timezone.make_aware(datetime(2020, 1, 1, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 1, 16))
        end_of_day = time(hour=16)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)

        overtime_generated = timedelta(hours=1)
        self.assertEqual(timeModel.overtime, overtime_generated)

    def test_time_evening(self):
        start_time = timezone.make_aware(datetime(2020, 1, 1, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 1, 16))
        end_of_day = time(hour=15)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)

        evening_generated = timedelta(hours=1)
        self.assertEqual(timeModel.evening, evening_generated)

    def test_time_weekend(self):
        start_time = timezone.make_aware(datetime(2020, 1, 4, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 4, 15))
        end_of_day = time(hour=15)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)

        weekend_generated = timedelta(hours=8)
        self.assertEqual(timeModel.weekend, weekend_generated)

    def test_time_holiday(self):
        start_time = timezone.make_aware(datetime(2020, 1, 1, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 1, 15))
        end_of_day = time(hour=15)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)

        holiday_generated = timedelta(hours=8)
        self.assertEqual(timeModel.holiday, holiday_generated)

    def test_time_holiday_sunday(self):
        start_time = timezone.make_aware(datetime(2020, 1, 5, 7))
        end_time = timezone.make_aware(datetime(2020, 1, 5, 15))
        end_of_day = time(hour=15)
        timeModel = Time(start_time=start_time, end_time=end_time)
        overtime = timedelta(hours=8)
        timeModel.check_additional(overtime, end_of_day)

        holiday_generated = timedelta(hours=0)
        self.assertEqual(timeModel.holiday, holiday_generated)

class PaycheckModelTest(TestCase):

    def test_paycheck_wage(self):
        pc = PayCheck()
        pc.set_wage(1000)

        self.assertEqual(pc.wage, 750)