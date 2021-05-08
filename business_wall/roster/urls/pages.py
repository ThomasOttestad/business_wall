from django.urls import path
from roster.views.pages import *
from roster.feeds.roster import RosterFeed, RosterFeedDepartment, RosterFeedWorker
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('calendar/', login_required(ReadOnlyCalendarView.as_view()), name="calendar"),
    path("editor", login_required(RosterEditorView.as_view()), name="roster_editor"),
    path('calendar/<int:uid>', login_required(ReadOnlyCalendarView.as_view())),
    path("shifts/<int:sid>/trade", login_required(ShiftTradeView.as_view())),


    path("shifts/trades/pending", login_required(ShiftTradePending.as_view()), name="pending"),
    path("shifts/trades/requested", login_required(ShiftTradeRequested.as_view()), name="requested"),
    path("shifts/trades/declined", login_required(ShiftTradeDeclined.as_view()), name="declined"),
    path("shifts/trades/accepted", login_required(ShiftTradeAccepted.as_view()), name="accepted"),

    path("shifts/trades/<int:tid>/answer", login_required(ShiftTradeAnswerView.as_view()), name="answer"),
    path('feed/calendar.ics', login_required(RosterFeed()), name="shift_feed_all"),
    path('feed/department/<int:did>/calendar.ics', login_required(RosterFeedDepartment()), name="shift_feed_department"),
    path('feed/worker/<int:uid>/calendar.ics', login_required(RosterFeedWorker()), name="shift_feed_worker"),
]
