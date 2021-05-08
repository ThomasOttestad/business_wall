from django import forms
from. import models




class schema_form(forms.ModelForm):
    # post = forms.CharField(widget=forms.TextInput(
    #     attrs={  
    #         'class': 'form-control',
    #     }
    # ))

    class Meta:
        model = models.Schema
        fields = ['issue','content']



    # sender_name = forms.CharField(label='Sender name', max_length=100)
    # category = forms.CharField(label='catergory', max_length=100)
    # text = forms.CharField(widget=forms.Textarea)
    