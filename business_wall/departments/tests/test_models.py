from django.test import TestCase
from django.core.exceptions import ValidationError
from departments.models import Department
from django.core.management import call_command
from accounts.util import create_user

class DepartmentModelTest(TestCase):
    def test_Department_name_duplicate_invalid(self):
        department = Department.objects.create(name="Office")
        with self.assertRaises(ValidationError):
            dup_department = Department(name="Office")
            dup_department.validate_unique()

    def test_department_name_length_invalid(self):
        with self.assertRaises(ValidationError):
            invalid_len = Department(name="t"*151)
            invalid_len.full_clean()

    def test_department_users_add(self):
        call_command("create_groups")
        supervisor = create_user("__all__", username="supervisor", password="raweogihrwr")
        worker = create_user(["worker"], username="worker", password="raweogihrwr")

        department = Department.objects.create(name="Office")
        department.users.add(supervisor, worker)
        self.assertListEqual(list(department.users.all()), [supervisor, worker])
