from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group, Permission
from django.core.management import call_command
from django.utils.timezone import make_aware
from roster.models import Shift
from departments.models import Department
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from accounts.util import create_user
from timesheet.models import AdditionalRate

def login_driver(driver, username, password):
    try:
        elem = driver.find_element_by_name("username")
        elem.send_keys(username)

        elem = driver.find_element_by_name("password")
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)
    except Exception as e:
        return False
    return True

def create_shifts(shifts=[]):
    for shift in shifts:
        Shift.objects.create(**shift)

def this_monday():
    n = datetime.now()
    return datetime(n.year, n.month, n.day, 12) + timedelta(days=-n.weekday())

class PageViewTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()

    def setUp(self):
        call_command("create_groups")
        AdditionalRate.objects.create()
        self.department = Department.objects.create(name="Office")
        self.worker = create_user(["worker"], username="worker", password="very_secure")
        self.shift_leader = create_user(["shift_leader", "supervisor"], username="shift_leader", password="very_secure")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

class ShowShiftsPageTest(PageViewTest):
    def test_show_shifts_acceptance(self):
        m = make_aware(this_monday())
        try:
            create_shifts([
                {
                    "department": self.department,
                    "worker": self.worker,
                    "shift_leader": self.shift_leader,
                    "start": m + timedelta(hours=24*day)
                } for day in range(5)
            ])
        except Exception as e:
            pass

        r = self.selenium.get(self.live_server_url + "/roster/calendar")
        if login_driver(self.selenium, "shift_leader", "very_secure"):
            time.sleep(1)
        week_count = self.selenium.find_elements_by_class_name("fc-list-item")
        time.sleep(1)
        self.assertEqual(len(week_count), 5)

        btn = self.selenium.find_element_by_class_name("fc-month-button")
        btn.click()
        time.sleep(1)
        month_count = self.selenium.find_elements_by_class_name("fc-event-container")
        time.sleep(1)
        self.assertEqual(len(month_count), 5)
