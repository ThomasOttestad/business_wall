from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    note = forms.CharField(label='')
    class Meta:
        model = Note
        fields = ['note']