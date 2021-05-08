from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from inbox.models import Message

class SendMessage(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SendMessage, self).__init__(*args, **kwargs)

        # So the field label makes sense in HTML
        self.fields['multiple_receivers'].label = "To"
        self.fields['msg_title'].label = "Title"
        self.fields['msg_content'].label = "Content"

        # Set 'to' field as a required field
        self.fields['multiple_receivers'].required = True

    class Meta:
        model = Message
        fields = ('multiple_receivers', 'msg_title', 'msg_content')

    def clean(self):
        cleaned_data = super().clean()
        to_user = cleaned_data.get("multiple_receivers")
        
        if to_user:
            if "@" not in to_user:
                raise forms.ValidationError(
                    "You need to enter a valid email address"
                )
        return cleaned_data


        