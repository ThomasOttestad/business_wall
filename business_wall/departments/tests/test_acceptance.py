from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.utils.timezone import make_aware
from departments.models import Department
from timesheet.models import AdditionalRate
from accounts.util import create_user
from departments.util import create_department
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time

class DepartmentAcceptanceTest(StaticLiveServerTestCase):
    DEPARTMENT_NAME = "Office"
    UPDATED_DEPARTMENT_NAME = "Register"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()

    def setUp(self):
        call_command("create_groups")
        AdditionalRate.objects.create()
        self.supervisor = create_user(["supervisor"], username="supervisor", password="very_secure")
        self.worker = create_user(["worker"], username="worker", password="very_secure")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def login(self, username, password):
        try:
            elem = self.selenium.find_element_by_name("username")
            elem.send_keys(username)

            elem = self.selenium.find_element_by_name("password")
            elem.send_keys(password)
            elem.send_keys(Keys.RETURN)
        except Exception as e:
            self.assertTrue(False, "Failed to login")

    def test_department_new_view(self):
        r = self.selenium.get(self.live_server_url + "/departments")
        self.login("supervisor", "very_secure")
        time.sleep(1)

        link = self.selenium.find_element_by_id("new_department")
        link.click()

        # Type department name
        name = self.selenium.find_element_by_id("id_name")
        name.send_keys(self.DEPARTMENT_NAME)
        time.sleep(1)

        # Select manager
        manager = Select(self.selenium.find_element_by_id("id_manager"))
        manager.select_by_visible_text(str(self.supervisor))
        time.sleep(1)

        # Select users
        users = Select(self.selenium.find_element_by_id("id_users"))
        users.select_by_visible_text(str(self.supervisor))
        time.sleep(1)

        # Submit
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(1)

        # Check that department exists
        table = self.selenium.find_element_by_id("department_table")
        name = table.find_element_by_xpath("//tbody/tr[1]/th[1]").text
        manager = table.find_element_by_xpath("//tbody/tr[1]/td[1]").text
        users = int(table.find_element_by_xpath("//tbody/tr[1]/td[2]").text)

        self.assertEqual(name, self.DEPARTMENT_NAME)
        self.assertEqual(manager, str(self.supervisor))
        self.assertEqual(1, users)

        # Check that the department messageboard exists
        self.selenium.get(self.live_server_url + "/messageboards/board")
        time.sleep(1)
        department = self.selenium.find_element_by_link_text(self.DEPARTMENT_NAME)
        self.assertTrue(bool(department), "Could not find department messageboard.")

    def test_department_update_name(self):
        create_department(users=[self.supervisor], manager=self.supervisor, name=self.DEPARTMENT_NAME)

        r = self.selenium.get(self.live_server_url + "/departments")
        self.login("supervisor", "very_secure")
        time.sleep(1)

        self.selenium.find_element_by_link_text(self.DEPARTMENT_NAME).click()
        time.sleep(1)

        self.selenium.find_element_by_id("update").click()
        time.sleep(1)

        elem = self.selenium.find_element_by_name("name")
        elem.clear()
        elem.send_keys(self.UPDATED_DEPARTMENT_NAME)
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(1)

        # Check that department name was updated
        name = self.selenium.find_element_by_xpath("//tbody/tr[1]/th[1]").text
        self.assertEqual(name, self.UPDATED_DEPARTMENT_NAME)

        self.selenium.get(self.live_server_url + "/messageboards/board")
        time.sleep(1)
        department = self.selenium.find_element_by_link_text(self.UPDATED_DEPARTMENT_NAME)
        self.assertTrue(bool(department), "Department messageboard name was not updated.")

    def test_department_delete(self):
        create_department(users=[self.supervisor], manager=self.supervisor, name=self.DEPARTMENT_NAME)

        r = self.selenium.get(self.live_server_url + "/departments")
        self.login("supervisor", "very_secure")
        time.sleep(1)

        self.selenium.find_element_by_link_text(self.DEPARTMENT_NAME).click()
        time.sleep(1)

        self.selenium.find_element_by_id("delete").click()
        time.sleep(1)

        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(1)

        with self.assertRaises(NoSuchElementException, msg="Department was not deleted"):
            department = self.selenium.find_element_by_xpath("//tbody/tr[1]")

    def test_department_add_user(self):
        create_department(users=[self.supervisor], manager=self.supervisor, name=self.DEPARTMENT_NAME)

        r = self.selenium.get(self.live_server_url + "/departments")
        self.login("supervisor", "very_secure")
        time.sleep(1)

        self.selenium.find_element_by_link_text(self.DEPARTMENT_NAME).click()
        time.sleep(1)

        self.selenium.find_element_by_id("add_user").click()
        time.sleep(1)

        # Select users
        users = Select(self.selenium.find_element_by_id("id_users"))
        users.select_by_visible_text(str(self.worker))
        time.sleep(1)

        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(1)

        users = int(self.selenium.find_element_by_xpath("//tbody/tr[1]/td[2]").text)
        self.assertEqual(2, users)

    def test_department_remove_user(self):
        create_department(users=[self.supervisor], manager=self.supervisor, name=self.DEPARTMENT_NAME)

        r = self.selenium.get(self.live_server_url + "/departments")
        self.login("supervisor", "very_secure")
        time.sleep(1)

        self.selenium.find_element_by_link_text(self.DEPARTMENT_NAME).click()
        time.sleep(1)

        self.selenium.find_element_by_id(f"remove_{self.supervisor.pk}").click()
        time.sleep(1)

        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(1)

        users = int(self.selenium.find_element_by_xpath("//tbody/tr[1]/td[2]").text)
        self.assertEqual(0, users)
