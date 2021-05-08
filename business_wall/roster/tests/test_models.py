from django.test import TestCase
from roster.models import Shift, ShiftTrade
from departments.models import Department
from accounts.util import create_user
from departments.util import create_department
from django.core.management import call_command
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


class ShiftModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("create_groups")
        cls.worker = create_user(groups=["worker"], username="worker", password="top_secret")
        cls.supervisor = create_user(groups="__all__", username="supervisor", password="top_secret")

        cls.department = create_department(users=[cls.supervisor, cls.worker], name="Office")

        cls.start = make_aware(datetime(2020, 1, 16, hour=12))

    def test_shift_model_generate_event(self):
        shift = Shift.objects.create(
            department=self.department,
            worker=self.worker,
            shift_leader=self.supervisor,
            start=self.start
        )

        ev = shift.generate_event()
        keys = [
            "id",
            "worker",
            "title",
            "start",
            "end",
            "organizer",
            "location",
            "color"
        ]

        self.assertListEqual(keys, list(ev.keys()))


class ShiftTradeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("create_groups")
        cls.worker1 = create_user(groups=["worker"], username="worker1", password="top_secret")
        cls.worker2 = create_user(groups=["worker"], username="worker2", password="top_secret")
        cls.supervisor = create_user(groups="__all__", username="supervisor", password="top_secret")

        cls.department = create_department(users=[cls.supervisor, cls.worker1, cls.worker2], name="Office")

        cls.shift = Shift.objects.create(
            department=cls.department,
            worker=cls.worker1,
            shift_leader=cls.supervisor,
            start=make_aware(datetime(2020, 1, 16, hour=12))
        )

    # def test_shift_trade_advance(self):
    #     trade = ShiftTrade.objects.create(shift=self.shift, trader=self.worker1, recipient=self.worker2, supervisor=self.supervisor)
    #
    #     self.assertEqual(trade.state, ShiftTradeState.RECIPIENT)
    #
    #     # Advance and make sure shift did not change worker yet
    #     self.assertEqual(trade.advance(), ShiftTradeState.SUPERVISOR)
    #     self.assertEqual(trade.shift.worker, trade.trader)
    #
    #     # Advance and make sure shift changed worker
    #     self.assertEqual(trade.advance(), ShiftTradeState.ACCEPTED)
    #     self.assertEqual(trade.shift.worker, trade.recipient)
    #
    # def test_shift_trade_revert(self):
    #     trade = ShiftTrade.objects.create(shift=self.shift, trader=self.worker1, recipient=self.worker2, supervisor=self.supervisor)
    #     trade.advance()
    #     trade.advance()
    #
    #     self.assertEqual(trade.shift.worker, trade.recipient)
    #
    #     self.assertEqual(trade.revert(), ShiftTradeState.REVERTED)
    #     self.assertEqual(trade.shift.worker, trade.trader)
