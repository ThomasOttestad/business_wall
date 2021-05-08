from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from . import forms
from .models import Schema
from django.contrib import messages


# Create your views here.


@login_required(login_url="/accounts/login/")
def schema_home(request):
    # return HttpResponse("something is returned")
    # return render(request, 'schemas/schema_home.html')

    form = forms.schema_form()
    return render(request, 'schemas/schema_home.html', {'form':form})

    # if request.method == 'POST':
    #     form = forms.schema_form(request.POST)

    #     if form.is_valid():
    #         return HttpResponse('/submitted/')

    # else:
    #     form = forms.schema_form()

    # return render(request, 'schemas/schema_home.html', {'form': form})
    
def submit_schema(request):
    pass

def post(request):
    pass


#@login_required
def create_schema(request):
    if request.method == 'POST':
        form = forms.schema_form(request.POST)
        if form.is_valid():
            #save to database
            instance = form.save(commit=False)
            instance.poster = request.user
            instance.save()
            return redirect('schema:home')

    else:
        form = forms.schema_form()
    
    return render(request, 'schemas/schema_home.html', {'form': form})
    



def list_schema(request):
    output_schema_list = Schema.objects.all()
    context = {"object_list": output_schema_list}
    return render(request, 'schemas/schema_list.html',context)


