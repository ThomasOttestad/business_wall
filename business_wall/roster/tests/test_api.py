from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from django.contrib.auth.models import User, Group, Permission
from django.core.management import call_command
from roster.models import Shift
from departments.models import Department
from datetime import datetime, timedelta
from accounts.util import create_user
import json

class ShiftApiTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ShiftApiTest, cls).setUpClass()
        call_command("create_groups")
        cls.department = Department.objects.create(name="office")
        cls.worker = create_user(["worker"], username="worker", password="very_secure")
        cls.shift_leader = create_user(["shift_leader", "supervisor"], username="shift_leader", password="very_secure")
        cls.unauthorized = create_user([], username="unauthorized", password="very_secure")

        cls.s1_start = make_aware(datetime(2020, 1, 16, hour=12))
        cls.s2_start = make_aware(datetime(2020, 1, 16, hour=8))

        cls.c = Client()
        l = cls.c.login(username="shift_leader", password="very_secure")

class GetShiftApiTest(ShiftApiTest):
    def test_shift_get(self):
        response = self.c.get("/api/shifts", {
            "start": self.s1_start,
            "end": self.s2_start
        })
        self.assertEqual(response.status_code, 200, response.content)

    def test_shift_get_invalid_date(self):
        response = self.c.get("/api/shifts", {
            "start": "qwerty",
            "end": self.s2_start
        })
        self.assertEqual(response.status_code, 400, response.content)

    def test_shift_get_unathorized(self):
        self.c = Client()
        l = self.c.login(username="unauthorized", password="very_secure")
        self.assertEqual(l, True, "Failed to login")

        response = self.c.get("/api/shifts", {
            "start": self.s1_start,
            "end": self.s2_start
        })
        self.assertEqual(response.status_code, 401, response.content)

class NewShiftApiTest(ShiftApiTest):
    def test_shift_new(self):
        response = self.c.post("/api/shifts", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
        })
        self.assertEqual(response.status_code, 200, response.content)

    def test_shift_new_unauthorized(self):
        self.c = Client()
        l = self.c.login(username="unauthorized", password="very_secure")
        self.assertEqual(l, True, "Failed to login")

        response = self.c.post("/api/shifts", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
        })
        self.assertEqual(response.status_code, 401, response.content)


    def test_shift_new_start_overlap(self):
        Shift.objects.create(worker=self.worker, shift_leader=self.shift_leader, start=self.s1_start, department=self.department)

        response = self.c.post("/api/shifts", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s2_start.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 400, response.content)
        try:
            body = json.loads(response.content)
            start_err = body["validationErrors"]["start"]
            self.assertListEqual(start_err, ["Overlapping shifts."])
        except KeyError as e:
            self.assertEqual(1,1)

    def test_shift_new_invalid_date(self):
        response = self.c.post("/api/shifts", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%d-%m-%Y %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_shift_new_invalid_worker(self):
        response = self.c.post("/api/shifts", {
            "worker": self.shift_leader.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_shift_new_invalid_shift_leader(self):
        response = self.c.post("/api/shifts", {
            "worker": self.worker.id,
            "shift_leader": self.worker.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 400, response.content)

class EditShiftApiTest(ShiftApiTest):
    def test_shift_edit(self):
        Shift.objects.create(worker=self.worker, shift_leader=self.shift_leader, start=self.s1_start, department=self.department)

        response = self.c.post("/api/shifts/1", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s2_start.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_shift_edit_unauthorized(self):
        self.c = Client()
        l = self.c.login(username="unauthorized", password="very_secure")
        self.assertEqual(l, True, "Failed to login")

        response = self.c.post("/api/shifts/1", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
        })
        self.assertEqual(response.status_code, 401, response.content)

    def test_shift_edit_nonexistant(self):
        response = self.c.post("/api/shifts/1", {
            "worker": self.worker.id,
            "shift_leader": self.shift_leader.id,
            "department": self.department.id,
            "start": self.s1_start.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertEqual(response.status_code, 404, response.content)
