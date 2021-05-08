from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User, Group, Permission
from django.core.management import call_command
from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
from accounts.util import create_user
from timesheet.models import Time, Stamp, PayCheck, AdditionalRate
from roster.models import Shift, Department

def login_driver(driver, username, password):
    try: 
        element = driver.find_element_by_name('username')
        element.send_keys(username)

        element = driver.find_element_by_name('password')
        element.send_keys(password)
        element.send_keys(Keys.RETURN)
    
    except Exception as e:
        return False
    return True

def create_time(date, start, duration):
    n = datetime.now()
    s = make_aware(datetime(n.year, n.month, date, start))
    e = make_aware(datetime(n.year, n.month, date, start + duration))
    return Time.objects.create(start_time=s, end_time=e)

def create_timesheet(stamp, full_month=False):
    n = datetime.now()

    # Adding a week, normal shift hours
    for i in range(1, 8, 1):
        stamp.time_model.add(create_time(i, 8, 8))


    if full_month: # pragma: no cover
        # Adding weekends
        for i in range(7, 15, 1): 
            get_day = datetime(n.year, n.month, i ,7)
            if get_day.isoweekday() is 6 or get_day.isoweekday() is 7:
                stamp.time_model.add(create_time(i, 8, 5))
        
        # Adding overtime
        for i in range(15, 22, 1):
            get_day = datetime(n.year, n.month, i, 7)
            if get_day.isoweekday() is not 6 and get_day.isoweekday() is not 7:
                stamp.time_model.add(create_time(i, 5, 10))

        # Adding evenings
        for i in range(22, 28, 1):
            get_day = datetime(n.year, n.month, i, 7)
            if get_day.isoweekday() is not 6 and get_day.isoweekday() is not 7:
                stamp.time_model.add(create_time(i, 17, 5))


def create_shifts(shifts=[]):
    for shift in shifts:
        Shift.objects.create(**shift)

def this_monday():
    n = datetime.now()
    return datetime(n.year, n.month, n.day, 12) + timedelta(days=-n.weekday())
class setUpTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()

    def setUp(self):
        AdditionalRate.objects.create()
        call_command('create_groups')
        self.worker = create_user(['worker'], username='worker', password='sdghdfutrh')
        stamp = Stamp.objects.get(worker=self.worker.id)
        create_timesheet(stamp)

        self.shift_leader = create_user(['shift_leader'], username='shift_leader', password='sdghdfutrh')
        stamp = Stamp.objects.get(worker=self.shift_leader.id)
        create_timesheet(stamp)
        
        self.supervisor = create_user(['supervisor'], username='supervisor', password='sdghdfutrh')
        stamp = Stamp.objects.get(worker=self.supervisor.id)
        create_timesheet(stamp)

        self.department = Department.objects.create(name="Office")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

class ShowTimesheetPage(setUpTestCase):
    def test_timesheet_edit_note(self):
        m = make_aware(this_monday())
        try:
            create_shifts([
                {
                    "department": self.department,
                    "worker": self.shift_leader,
                    "shift_leader": self.shift_leader,
                    "start": m + timedelta(hours=24*day)
                } for day in range(5)
            ])
        except Exception as e:
            pass



        r = self.selenium.get(self.live_server_url + '/timesheet')
        if login_driver(self.selenium, 'shift_leader', 'sdghdfutrh'):
            time.sleep(1)
        
        btn = self.selenium.find_element_by_name('edit_note')
        
        btn.click()
        note = 'some note'
        time.sleep(1)

        elem = self.selenium.find_element_by_css_selector('textarea')
        elem.send_keys(note)
        time.sleep(1)

        btn = self.selenium.find_element_by_name('save')
        btn.click()
        time.sleep(1)

        self.assertEqual(note, Time.objects.get(id=8).note)

        self.selenium.find_element_by_name('edit_timesheet').click()

        n = datetime.now()

        start = str(n.year) + '-' + f'{n:%m}' + '-' + '01' + ' ' + '07:00'
        end = str(n.year) + '-' + f'{n:%m}' + '-' + '01' + ' ' + '15:00'

        btn = self.selenium.find_element_by_name('edit_time')
        btn.click()
        time.sleep(1)

        elem = self.selenium.find_element_by_name('start_time')
        elem.clear()
        time.sleep(1)
        elem.send_keys(start)
        time.sleep(1)

        elem = self.selenium.find_element_by_name('end_time')
        elem.clear()
        time.sleep(1)
        elem.send_keys(end)
        time.sleep(1)

        btn = self.selenium.find_element_by_name('time_save')
        btn.click()
        time.sleep(1)

        start = make_aware(datetime(n.year, n.month, 1, 7))
        end = make_aware(datetime(n.year, n.month, 1, 15))

        self.assertEqual(start, Time.objects.get(id=8).start_time)

        self.assertEqual(end, Time.objects.get(id=8).end_time)

        self.selenium.get(self.live_server_url + '/profile/userprofile')

        self.selenium.find_element_by_name('paycheck').click()
        time.sleep(1)

        self.selenium.find_element_by_name('estimate_paycheck').click()
        time.sleep(1)