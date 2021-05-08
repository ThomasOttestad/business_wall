from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from roster.models import Shift, ShiftTrade
from roster.forms import ShiftForm, ShiftTradeForm, ShiftTradeAnswerForm
from django.views import View
from departments.models import Department
from django.contrib.auth.models import User

from django.db.models import Q

class ReadOnlyCalendarView(View):
    def get(self, request, uid=None, *args, **kwargs):
        departments = Department.objects.filter(users__id=request.user.id)

        return render(request, 'calendar.html', {
            "user": request.user,
            "departments": departments,
            "eventUrl": "/api/shifts"
        })

class RosterEditorView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=["supervisor"]):
            return redirect("calendar")
        return render(request, 'roster_editor.html', {"form": ShiftForm()})

class ShiftTradeView(View):
    def get(self, request, sid, *args, **kwargs):
        shift = get_object_or_404(Shift, pk=sid)
        if shift.worker != request.user:
            return render(request, "401.html")
        form = ShiftTradeForm(shift=shift, trader=request.user)
        return render(request, "new_shift_trade.html", {"form": form, "shift": shift})

    def post(self, request, sid, *args, **kwargs):
        shift = get_object_or_404(Shift, pk=sid)
        if shift.worker != request.user:
            return render(request, "401.html", status=401)
        trade = ShiftTradeForm({**request.POST.dict(), "shift": shift, "trader": request.user})
        if trade.is_valid():
            trade.save()
            return redirect("calendar")
        return render(request, "new_shift_trade.html", {"form": trade, "shift": shift})

class ShiftTradeAnswerView(View):
    def get_correct_response(self, trade, context):
        if self.request.user == trade.supervisor:
            return render(self.request, "trades/answer/supervisor.html", context)
        elif self.request.user == trade.recipient:
            return render(self.request, "trades/answer/recipient.html", context)
        else:
            return render(self.request, "401.html", status=401)


    def get(self, request, tid, *args, **kwargs):
        trade = get_object_or_404(ShiftTrade, pk=tid)
        form = ShiftTradeAnswerForm(trade, request.user)
        return self.get_correct_response(trade, {"trade": trade, "user": request.user, "form": form})

    def post(self, request, tid, *args, **kwargs):
        trade = get_object_or_404(ShiftTrade, pk=tid)
        if request.user not in [trade.recipient, trade.supervisor]:
            return render(request, "401.html", status=401)

        form = ShiftTradeAnswerForm(trade, request.user, request.POST)
        if form.is_valid():
            form.save()
        return self.get_correct_response(trade, {"trade": trade, "user": request.user, "form": form})

class ShiftTradePending(View):
    def get(self, request, *args, **kwargs):
        return render(request, "trades/pending.html", {"pending": request.user.pending_trades()})

class ShiftTradeRequested(View):
    def get(self, request, *args, **kwargs):
        return render(request, "trades/requested.html", {"requested": request.user.requested_trades()})

class ShiftTradeDeclined(View):
    def get(self, request, *args, **kwargs):
        return render(request, "trades/declined.html", {"declined": request.user.declined_trades()})

class ShiftTradeAccepted(View):
    def get(self, request, *args, **kwargs):
        return render(request, "trades/accepted.html", {"accepted": request.user.accepted_trades()})
