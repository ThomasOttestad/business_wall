from django.test import TestCase, Client, RequestFactory
from timesheet.models import Time, Stamp, AdditionalRate, PayCheck
from timesheet.views import stamp_in, stamp_out, timesheet_view, edit_timesheet
from timesheet.views import edit_note, edit_time, generate_paycheck
from userprofile.models import Contract
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from datetime import datetime
from django.utils import timezone


class setUpTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('create_groups')
        w = User.objects.create(username='worker', password='sdghdfutrh')
        w.set_password('sdghdfutrh')
        w.groups.set([Group.objects.get(name='worker')])
        w.save()
        
        sl = User.objects.create(username='shift_leader', password='sdghdfutrh')
        sl.set_password('sdghdfutrh')
        sl.groups.set(Group.objects.filter(name__in=['shift_leader', 'supervisor']))
        sl.save()

    def setUp(self):
        self.worker = User.objects.get(username="worker")
        self.shift_leader = User.objects.get(username="shift_leader")

        self.c = Client()
        self.factory = RequestFactory()
        l = self.c.login(username='shift_leader', password='sdghdfutrh')
        self.assertEqual(l, True, 'Failed to login')
        self.ar = AdditionalRate()
        self.ar.save()
    

class StampViewTest(setUpTestCase):
    def test_stamp_stampin(self):
        self.c.login(username='worker', password='sdghdfutrh')
        Stamp.objects.create(worker=self.worker, additonal_rate=self.ar)
        request = self.factory.post('/timesheet/stampin')
        request.user = self.worker

        stamp_in(request)
        stamp = Stamp.objects.get(worker=self.worker.id)
        
        self.assertEqual(stamp.stampedIn, True)

    def test_stamp_stampout(self):
        self.c.login(username='worker', password='sdghdfutrh')
        Stamp.objects.create(worker=self.worker, additonal_rate=self.ar)

        request = self.factory.post('/timesheet/stampin')
        request.user = self.worker

        stamp_out(request)
        stamp = Stamp.objects.get(worker=self.worker.id)
        
        self.assertEqual(stamp.stampedIn, False)


    def test_timesheet_view(self):
        self.c.login(username='worker', password='sdghdfutrh')
        Stamp.objects.create(worker=self.worker, additonal_rate=self.ar)

        request = self.c.post('/timesheet/')
        request.user = self.worker
        self.assertEqual(request.status_code, 200)


class PaycheckViewTest(setUpTestCase):
    def test_generate_paycheck(self):
        self.c.login(username='worker', password='sdghdfutrh')
        stamp = Stamp.objects.create(worker=self.worker, additonal_rate=self.ar)
        pc = PayCheck.objects.create(worker=self.worker)
        Contract.objects.create(worker=self.worker)
        
        s1 = timezone.make_aware(datetime(2020, 3, 1, 8))
        e1 = timezone.make_aware(datetime(2020, 3, 1, 16))

        s2 = timezone.make_aware(datetime(2020, 3, 2, 8))
        e2 = timezone.make_aware(datetime(2020, 3, 2, 16))

        s3 = timezone.make_aware(datetime(2020, 3, 3, 8))
        e3 = timezone.make_aware(datetime(2020, 3, 3, 18))

        s4 = timezone.make_aware(datetime(2020, 3, 4, 8))
        e4 = timezone.make_aware(datetime(2020, 3, 4, 14))

        t1 = Time.objects.create(start_time=s1, end_time=e1)
        t2 = Time.objects.create(start_time=s2, end_time=e2)
        t3 = Time.objects.create(start_time=s3, end_time=e3)
        t4 = Time.objects.create(start_time=s4, end_time=e4)

        stamp.time_model.add(t1)
        stamp.time_model.add(t2)
        stamp.time_model.add(t3)

        request = self.c.post('/timesheet/paycheck/')
        request.user = self.worker

        self.assertEqual(request.status_code, 200)