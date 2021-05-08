from django.shortcuts import render
from django import forms
from messageboard.models import Board, Topic, Post
from departments.models import Department
from timesheet.models import Stamp
from datetime import datetime
from django.contrib.auth.models import User

def homepage(request):
    today = datetime.now()

    groups = request.user.groups.filter(name="supervisor")
    
    if len(groups) > 0:
        posts = Post.objects.filter(topic__pinned=True, reply=False).order_by('-created_at')[:4]
    else:
        #det her funker ganske dårlig, eller ikkje
        #prøver å filtere vekk de post.topic.board.pk som ikke e i boardquery.pk men funke jevla dårlig
        queryset = Department.objects.exclude(users=request.user)
        boardquery = Board.objects.exclude(pk__in=[q.board.pk for q in queryset])
        posts = Post.objects.filter(topic__board__pk__in=[i.pk for i in boardquery], topic__pinned=True, reply=False).order_by('-created_at')[:4]

    stamp_info = Stamp.objects.get(worker=request.user.id)
    time_order = stamp_info.time_model.order_by('start_time')
    todays_stamps = time_order.filter(start_time__day=today.day, start_time__month=today.month, start_time__year=today.year).reverse()[:3]

    context = { 'user': request.user,
                'stampUser':stamp_info,
                'time':todays_stamps,
                "posts": posts,
                "eventUrl": f"/api/shifts/user/{request.user.pk}"
    }

    return render(request, 'homepage.html', context)

def stamp_homepage(request):
    today = datetime.now()

    stamp_info = Stamp.objects.get(worker=request.user.id)
    time_order = stamp_info.time_model.order_by('start_time')
    todays_stamps = time_order.filter(start_time__day=today.day, start_time__month=today.month, start_time__year=today.year)

    context = { 'stampUser':stamp_info,
                'time':todays_stamps,
                }

    return render(request, 'example_homepage.html', context)
