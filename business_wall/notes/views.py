from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Note
from .forms import NoteForm

# Create your views here.

def index(request):
    item_list = Note.objects.order_by('date')

    context = {
        'list': item_list,
        'form': NoteForm(),
    }
    return render(request, 'note.html', context)

def add(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()

            return redirect('/notes', note.id)

def edit(request, id):
   
    item_list = Note.objects.get(pk=id)
    
    form = NoteForm(request.POST, instance=item_list)
    if form.is_valid():
        form.save()

    return redirect('/notes')