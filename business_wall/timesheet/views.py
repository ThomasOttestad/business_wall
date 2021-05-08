from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import Time, Stamp, PayCheck
from userprofile.models import Contract
from .forms import *
from datetime import timedelta, datetime
import calendar
from roster.models import Shift


def stamp_in(request):
    stamp = Stamp.objects.get(worker=request.user.id)
    if request.method == 'POST':
        if stamp.stampedIn == False:
            stamp.stampedIn = True
            time_stamped_in = Time.objects.create()
            stamp.time_model.add(time_stamped_in)
            stamp.save()

    return redirect('home')


def stamp_out(request):
    stamp = Stamp.objects.get(worker=request.user.id)
    if request.method == 'POST':
        if stamp.stampedIn == True:
            stamp.stampedIn = False
            stamp.set_end_time()
            stamp.save()

    return redirect('home')


def timesheet_view(request):
    today = datetime.now()
    if request.POST:
        form = CalenderPickerForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data.get('month'))
            year = form.cleaned_data.get('year')
        else:
            return redirect('timesheet')

    else:
        month = today.month
        year = today.year
        form = CalenderPickerForm(initial={'worker': request.user, 'month':month, 'year':year})


    if request.user.groups.filter(name__in=['shift_leader', 'supervisor']):
        has_perm = True
    else:
        has_perm = False

    stamping = Stamp.objects.get(worker=request.user.id)
    time_order = stamping.time_model.order_by('start_time')
    time = time_order.filter(start_time__month=month, start_time__year= year)

    sum_duration = timedelta(minutes=0)
    sum_overtime = timedelta(minutes=0)
    sum_evening = timedelta(minutes=0)
    sum_weekend = timedelta(minutes=0)
    sum_holiday = timedelta(minutes=0)

    for i in time:
        if i.end_time:
            i.check_additional(stamping.shift_duration, stamping.end_of_day)

        sum_duration += i.time_worked
        sum_overtime += i.overtime
        sum_evening += i.evening
        sum_weekend += i.weekend
        sum_holiday += i.holiday

    context = { 'time':time,
                'sum_duration':sum_duration,
                'sum_overtime':sum_overtime,
                'sum_evening':sum_evening,
                'sum_weekend':sum_weekend,
                'sum_holiday':sum_holiday,
                'noteForm':NoteForm(),
                'timeForm': TimeForm(),
                'calenderform':form,
                'curr_month':calendar.month_name[month],
                'curr_year':year,
                'has_perm':has_perm,
                }

    return render(request, 'timesheet.html', context)

def edit_timesheet(request, *args, **kwargs):
    today = datetime.now()
    # if request.user.groups.filter(name__in=['shift_leader', 'supervisor']):
    if request.POST:
        form = CalenderPickerForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data.get('month'))
            work = form.cleaned_data.get('worker')
            year = form.cleaned_data.get('year')
            worker = User.objects.get(username=work).id
        else:
            return redirect('edit_timesheet')
    else:
        month = today.month
        worker = request.user.id
        year = today.year
        form = CalenderPickerForm(initial={'worker':worker, 'year':year, 'month':month})

    stamping = Stamp.objects.get(worker=worker)
    time_order = stamping.time_model.order_by('start_time')
    time = time_order.filter(start_time__month=month, start_time__year=year)

    sum_duration = timedelta(minutes=0)
    sum_overtime = timedelta(minutes=0)
    sum_evening = timedelta(minutes=0)
    sum_weekend = timedelta(minutes=0)
    sum_holiday = timedelta(minutes=0)

    for i in time:
        if i.end_time:
            i.check_additional(stamping.shift_duration, stamping.end_of_day)

        sum_duration += i.time_worked
        sum_overtime += i.overtime
        sum_evening += i.evening
        sum_weekend += i.weekend
        sum_holiday += i.holiday

    if "timeFormData" in request.session:
        timeForm = TimeForm(request.session.pop("timeFormData"))
        timeForm.is_valid()
    else:
        timeForm = TimeForm()

    context = { 'time':time,
                'sum_duration':sum_duration,
                'sum_overtime':sum_overtime,
                'sum_evening':sum_evening,
                'sum_weekend':sum_weekend,
                'sum_holiday':sum_holiday,
                'noteForm':NoteForm(),
                'timeForm': timeForm,
                'calenderform':form,
                'curr_month':calendar.month_name[month],
                'curr_year':year,
                'worker':User.objects.get(id=worker),
                }

    return render(request, 'timesheet_edit.html', context)
    # else:
    #     return redirect('timesheet')

def edit_note(request, id):
    time = Time.objects.get(pk=id)
    form = NoteForm(request.POST, instance=time)
    if form.is_valid():
        form.save()

    return redirect('timesheet')



def edit_time(request, id):
    time = Time.objects.get(pk=id)
    if request.user.is_manager():
        form = TimeForm(request.POST, instance=time)
    else:
        form = TimeForm({"note": request.POST["note"]}, instance=time)

    if form.is_valid():
        form.save()

    request.session['timeFormData'] = request.POST

    return redirect('timesheet')

def convert_rate(rate):
    return 1 + (rate/100)

def find_holiday_pay(stamp, contract, paycheck, ar):
    today = datetime.now()

    time_order = stamp.time_model.order_by('start_time')

    sum_duration = timedelta(minutes=0)
    sum_overtime = timedelta(minutes=0)
    sum_evening = timedelta(minutes=0)
    sum_weekend = timedelta(minutes=0)
    sum_holiday = timedelta(minutes=0)

    for month in range(1, today.month + 1):
        time = time_order.filter(start_time__month=month, start_time__year=today.year)

        for i in time:
            if i.end_time:
                i.check_additional(stamp.shift_duration, stamp.end_of_day)

            sum_duration += i.find_sum()
            sum_overtime += i.overtime
            sum_evening += i.evening
            sum_weekend += i.weekend
            sum_holiday += i.holiday

    wage_from_normal = ((((sum_duration.seconds // 60) % 60) / 60) + (sum_duration.seconds // 3600) + sum_duration.days * 24) * convert_rate(ar.normal_rate)
    wage_from_overtime = (((((sum_overtime.seconds // 60) % 60) / 60) + (sum_overtime.seconds // 3600) + (sum_overtime.days * 24)) * convert_rate(ar.overtime_rate))
    wage_from_weekend = (((((sum_weekend.seconds // 60) % 60) / 60) + (sum_weekend.seconds // 3600) + (sum_weekend.days * 24)) * convert_rate(ar.weekend_rate))
    wage_from_evening = (((((sum_evening.seconds // 60) % 60) / 60) + (sum_evening.seconds // 3600) + (sum_evening.days * 24)) * convert_rate(ar.evening_rate))
    wage_from_holiday = (((((sum_holiday.seconds // 60) % 60) / 60) + (sum_holiday.seconds // 3600) + (sum_holiday.days * 24)) * convert_rate(ar.holiday_rate))
    wage_total  = wage_from_normal + wage_from_overtime + wage_from_weekend + wage_from_evening + wage_from_holiday
    wage = wage_total * contract.wage

    return ((paycheck.vacation_money_basis * wage) / 100)

def generate_estimate_times(start, duration, overtime, end_of_day):
    get_date = start.date()
    get_day = get_date.isoweekday()
    get_holidays = holidays.Norway(include_sundays=False)
    get_evening = timezone.make_aware(datetime.combine(get_date, end_of_day))


    tot_overtime = timedelta(minutes=0)
    tot_evening = timedelta(minutes=0)
    weekend = timedelta(minutes=0)
    tot_holiday = timedelta(minutes=0)
    tot_duration = duration

    if duration > overtime:
        tot_overtime = duration - overtime

    if start + duration > get_evening:
        if start.time() >= end_of_day:
            tot_evening = duration
        else:
            tot_evening = (start + duration) - get_evening

    if tot_overtime or tot_evening:
        if tot_overtime > tot_evening:
            tot_duration = duration - tot_overtime
        else:
            tot_duration = duration - tot_evening

    if get_day is 6 or get_day is 7:
        weekend = duration
        tot_duration = timedelta(minutes=0)

    if get_date in get_holidays:
        tot_holiday = duration
        tot_duration = timedelta(minutes=0)

    return tot_duration, tot_overtime, tot_evening, weekend, tot_holiday

def generate_paycheck(request):
    if request.POST:
        form = CalenderPickerForm(request.POST)
        if form.is_valid():
            month = int(form.cleaned_data.get('month'))
            year = int(form.cleaned_data.get('year'))

    else:
        today = datetime.now()
        month = today.month
        year = today.year
        form = CalenderPickerForm(initial={'month':month, 'year':year, 'worker':request.user.id})

    today = datetime.now()
    stamp = Stamp.objects.get(worker=request.user.id)
    time_order = stamp.time_model.order_by('start_time')
    time = time_order.filter(start_time__month=month, start_time__year=year)
    ar = stamp.additonal_rate
    paycheck = PayCheck.objects.get(worker=request.user.id)
    contract = Contract.objects.get(worker=request.user.id)

    sum_total_time = timedelta(minutes=0)
    sum_duration = timedelta(minutes=0)
    sum_overtime = timedelta(minutes=0)
    sum_evening = timedelta(minutes=0)
    sum_weekend = timedelta(minutes=0)
    sum_holiday = timedelta(minutes=0)

    for i in time:
        if i.end_time:
            i.check_additional(stamp.shift_duration, stamp.end_of_day)

        sum_total_time += i.time_worked
        sum_duration += i.find_sum()
        sum_overtime += i.overtime
        sum_evening += i.evening
        sum_weekend += i.weekend
        sum_holiday += i.holiday

    wage_from_normal = ((((sum_duration.seconds // 60) % 60) / 60) + (sum_duration.seconds // 3600) + sum_duration.days * 24) * convert_rate(ar.normal_rate)
    wage_from_overtime = (((((sum_overtime.seconds // 60) % 60) / 60) + (sum_overtime.seconds // 3600) + (sum_overtime.days * 24)) * convert_rate(ar.overtime_rate))
    wage_from_weekend = (((((sum_weekend.seconds // 60) % 60) / 60) + (sum_weekend.seconds // 3600) + (sum_weekend.days * 24)) * convert_rate(ar.weekend_rate))
    wage_from_evening = (((((sum_evening.seconds // 60) % 60) / 60) + (sum_evening.seconds // 3600) + (sum_evening.days * 24)) * convert_rate(ar.evening_rate))
    wage_from_holiday = (((((sum_holiday.seconds // 60) % 60) / 60) + (sum_holiday.seconds // 3600) + (sum_holiday.days * 24)) * convert_rate(ar.holiday_rate))
    wage_total  = wage_from_normal + wage_from_overtime + wage_from_weekend + wage_from_evening + wage_from_holiday
    wage = wage_total * contract.wage
    holiday_pay_basis = (paycheck.vacation_money_basis * wage) / 100
    paycheck.set_wage(wage - holiday_pay_basis)

    context = {'wage':round(wage, 1),
                'taxes': round(wage - paycheck.wage, 1),
                'contract':contract,
                'additional_rate': ar,
                'paycheck':paycheck,
                'calenderform':form,
                'vacation_money_basis': holiday_pay_basis,
                'tot_vac':find_holiday_pay(stamp, contract, paycheck, ar),
                'estimate':False,

                'sum_total_time':sum_total_time,
                'sum_duration':sum_duration,
                'sum_overtime':sum_overtime,
                'sum_holiday':sum_holiday,
                'sum_weekend':sum_weekend,
                'sum_evening':sum_evening,

                'rate_normal':round(convert_rate(ar.normal_rate) * contract.wage, 1),
                'rate_weekend':round(convert_rate(ar.weekend_rate) * contract.wage, 1),
                'rate_overtime':round(convert_rate(ar.overtime_rate) * contract.wage, 1),
                'rate_evening':round(convert_rate(ar.evening_rate) * contract.wage, 1),
                'rate_holiday':round(convert_rate(ar.holiday_rate) * contract.wage, 1),

                'amount_normal':round(wage_from_normal * contract.wage, 1),
                'amount_overtime':round(wage_from_overtime * contract.wage, 1),
                'amount_weekend':round(wage_from_weekend * contract.wage, 1),
                'amount_evening':round(wage_from_evening * contract.wage, 1),
                'amount_holiday':round(wage_from_holiday * contract.wage, 1),
                }

    return render(request, 'paycheck.html', context)

def estimate_paycheck(request):
    today = datetime.now()

    stamp = Stamp.objects.get(worker=request.user.id)
    paycheck = PayCheck.objects.get(worker=request.user.id)
    contract = Contract.objects.get(worker=request.user.id)
    shift = Shift.objects.filter(worker=request.user.id)

    ar = stamp.additonal_rate
    time_order = stamp.time_model.order_by('start_time')
    time = time_order.filter(start_time__month=today.month, start_time__year=today.year)

    sum_total_time = timedelta(minutes=0)
    sum_duration = timedelta(minutes=0)
    sum_overtime = timedelta(minutes=0)
    sum_evening = timedelta(minutes=0)
    sum_weekend = timedelta(minutes=0)
    sum_holiday = timedelta(minutes=0)

    for i in range(len(shift)):
        if not time.filter(start_time__day=shift[i].start.day ,start_time__month=shift[i].start.month, start_time__year=shift[i].start.year):
            tot_duration, tot_overtime, tot_evening, weekend, tot_holiday = generate_estimate_times(shift[i].start, shift[i].duration, stamp.shift_duration, stamp.end_of_day)

            sum_total_time += shift[i].duration
            sum_duration += tot_duration
            sum_overtime += tot_overtime
            sum_evening += tot_evening
            sum_weekend += weekend
            sum_holiday += tot_holiday

    for i in time:
        if i.end_time:
            i.check_additional(stamp.shift_duration, stamp.end_of_day)

        sum_total_time += i.time_worked
        sum_duration += i.find_sum()
        sum_overtime += i.overtime
        sum_evening += i.evening
        sum_weekend += i.weekend
        sum_holiday += i.holiday

    wage_from_normal = ((((sum_duration.seconds // 60) % 60) / 60) + (sum_duration.seconds // 3600) + sum_duration.days * 24) * convert_rate(ar.normal_rate)
    wage_from_overtime = (((((sum_overtime.seconds // 60) % 60) / 60) + (sum_overtime.seconds // 3600) + (sum_overtime.days * 24)) * convert_rate(ar.overtime_rate))
    wage_from_weekend = (((((sum_weekend.seconds // 60) % 60) / 60) + (sum_weekend.seconds // 3600) + (sum_weekend.days * 24)) * convert_rate(ar.weekend_rate))
    wage_from_evening = (((((sum_evening.seconds // 60) % 60) / 60) + (sum_evening.seconds // 3600) + (sum_evening.days * 24)) * convert_rate(ar.evening_rate))
    wage_from_holiday = (((((sum_holiday.seconds // 60) % 60) / 60) + (sum_holiday.seconds // 3600) + (sum_holiday.days * 24)) * convert_rate(ar.holiday_rate))
    wage_total  = wage_from_normal + wage_from_overtime + wage_from_weekend + wage_from_evening + wage_from_holiday
    wage = wage_total * contract.wage
    holiday_pay_basis = (paycheck.vacation_money_basis * wage) / 100
    paycheck.set_wage(wage - holiday_pay_basis)

    context = {'wage':round(wage, 1),
                'taxes': round(wage - paycheck.wage, 1),
                'contract':contract,
                'additional_rate': ar,
                'paycheck':paycheck,
                'vacation_money_basis': holiday_pay_basis,
                'tot_vac':find_holiday_pay(stamp, contract, paycheck, ar),
                'estimate':True,

                'sum_total_time':sum_total_time,
                'sum_duration':sum_duration,
                'sum_overtime':sum_overtime,
                'sum_holiday':sum_holiday,
                'sum_weekend':sum_weekend,
                'sum_evening':sum_evening,

                'rate_normal':round(convert_rate(ar.normal_rate) * contract.wage, 1),
                'rate_weekend':round(convert_rate(ar.weekend_rate) * contract.wage, 1),
                'rate_overtime':round(convert_rate(ar.overtime_rate) * contract.wage, 1),
                'rate_evening':round(convert_rate(ar.evening_rate) * contract.wage, 1),
                'rate_holiday':round(convert_rate(ar.holiday_rate) * contract.wage, 1),

                'amount_normal':round(wage_from_normal * contract.wage, 1),
                'amount_overtime':round(wage_from_overtime * contract.wage, 1),
                'amount_weekend':round(wage_from_weekend * contract.wage, 1),
                'amount_evening':round(wage_from_evening * contract.wage, 1),
                'amount_holiday':round(wage_from_holiday * contract.wage, 1),
                }

    return render(request, 'paycheck.html', context)


def create_time(date, start, duration): # pragma: no cover
    now = datetime.now()
    start_time = timezone.make_aware(datetime(now.year, now.month, date, start))
    end = timezone.make_aware(datetime(now.year, now.month, date, start + duration))
    return Time.objects.create(start_time=start_time, end_time=end)

def populate_database(request): # pragma: no cover
    now = datetime.now()
    stamp = Stamp.objects.get(worker=request.user.id)

    if stamp.time_model.count() is 0:
        # Adding a week, normal shift hours
        for i in range(1, 7, 1):
            date = datetime(now.year, now.month, i, 7)
            if date.isoweekday() is not 6 and date.isoweekday() is not 7:
                stamp.time_model.add(create_time(i, 8, 8))

        # Adding weekends
        for i in range(7, 15, 1):
            get_day = datetime(now.year, now.month, i ,7)
            if get_day.isoweekday() is 6 or get_day.isoweekday() is 7:
                stamp.time_model.add(create_time(i, 8, 5))

        # Adding overtime
        for i in range(15, 22, 1):
            get_day = datetime(now.year, now.month, i, 7)
            if get_day.isoweekday() is not 6 and get_day.isoweekday() is not 7:
                stamp.time_model.add(create_time(i, 5, 10))

        # Adding evenings
        for i in range(22, 28, 1):
            get_day = datetime(now.year, now.month, i, 7)
            if get_day.isoweekday() is not 6 and get_day.isoweekday() is not 7:
                stamp.time_model.add(create_time(i, 17, 5))

    return redirect('timesheet')
