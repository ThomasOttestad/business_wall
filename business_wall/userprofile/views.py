from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .forms import *
from timesheet.models import *
from messageboard.models import *
from .models import *
from datetime import datetime
from business_wall.settings import MEDIA_ROOT, MEDIA_URL
import os

def index(request):
    stampUser = Stamp.objects.get(worker=request.user.id)

    today = datetime.now()
    posts = Post.objects.filter(topic__original_poster=request.user).order_by('-created_at')[:4]



    return render(request, 'userprofile.html', {'stampUser': stampUser, 'posts': posts})

def upload(request):
    documents = Document.objects.all()
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('documents')

    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form, 'documents': documents})

def documents(request):
    documents = Document.objects.all()
    return render(request, 'documents.html', {'documents': documents})


def change(request):

    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES)
        sform = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():

            initial_obj = form.save(commit=False)
            initial_obj.save()

            print(initial_obj.Avatar_Main_Img.path)

            #file = form.cleaned_data['Avatar_Main_Img'].name
            #path = initial_obj.Avatar_Main_Img.path
            #path = os.path.join(location, file)
            #print("path is:", path)

            if os.path.isfile(initial_obj.Avatar_Main_Img.path):
                print("Path is found!")
                #os.remove(path)
            print(form.cleaned_data['Avatar_Main_Img'].name)
            form.image_name = form.cleaned_data['Avatar_Main_Img'].name
            form.save()
            return redirect('userprofile')
        if sform.is_valid():
            sform.save()
            return redirect('userprofile')

    else:
        form = AvatarForm(user=request.user)
        sform = PasswordChangeForm(request.user)
    return render(request, 'change.html', {'form' : AvatarForm(user=request.user), 'sform' : sform})
