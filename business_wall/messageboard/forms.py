from django import forms
from .models import Topic, Post, Board

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'Whats on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    class Meta:
        model = Topic
        fields = ['subject', 'message', 'pinned']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]
    
class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
