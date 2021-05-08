from django import forms
from .models import *
from django.contrib.auth.models import User


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document',)

class AvatarForm(forms.ModelForm):

    class Meta:
        model = Avatar
        fields = ('Avatar_Main_Img', "user")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super(AvatarForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["user"] = forms.ModelChoiceField(
            queryset = User.objects.filter(pk=user.pk),
            widget = forms.Select(attrs={"hidden": True}),
            initial = user
            )

    def save(self, *args, **kwargs):
        try:
            old = Avatar.objects.get(pk=self.cleaned_data["user"].pk)
            old.delete()
        except Exception as e:
            pass
        return super().save(*args, **kwargs)



# class PasswordForm(forms.ModelForm):

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')
