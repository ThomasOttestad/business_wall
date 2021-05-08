from django.test import TestCase
from django.core.management import call_command
from departments.models import Department
from accounts.util import create_user

class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("create_groups")
        cls.supervisor = create_user("__all__", username="supervisor", password="top_secret")
        cls.worker = create_user(["worker"], username="worker", password="top_secret")

    def setUp(self):
        l = self.client.login(username="supervisor", password="top_secret")
        self.assertEquals(l, True, "Failed to login supervisor.")

    def test_departments_view(self):
        department = Department.objects.create(name="Office")

        r = self.client.get("/departments/")
        self.assertContains(r, department.name)

    def test_department_supervisor_home_view(self):
        department = Department.objects.create(name="Office")
        department.users.add(self.supervisor)

        r = self.client.get(f"/departments/{department.pk}")
        self.assertContains(r, department.name)
        self.assertContains(r, self.supervisor)

    def test_department_worker_home_view(self):
        raise Exception()
