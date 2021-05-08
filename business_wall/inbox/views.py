from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Message
from django.contrib.auth.models import User
from .forms import SendMessage
import json
from django.http import JsonResponse, HttpRequest, Http404
from django.core.exceptions import ValidationError

# Populate inbox with messages to currently logged in user
def populate_inbox(request):
    for i in range(0, 10):
        new = Message.objects.create(
            sender=request.user, 
            receiver=request.user,
            msg_title='Title ' + str(i), 
            msg_content='Message content ' + str(i)
        )
        new.save()
    return redirect('/inbox')

# inbox view
def inbox(request):

    inbox = Message.objects.filter(receiver=request.user).order_by('-sent')
    sent_msg = Message.objects.filter(sender=request.user).order_by('-sent')
    all_users = User.objects.all()
    
    context = {
        'sent_message': sent_msg,
        'message': inbox,
        'users': all_users,
        'form': SendMessage(),
    }
    return render(request, 'inbox.html', context)

# Send a message to one or several users
def send_message(request):
    if request.method == 'POST':
        form = SendMessage(request.POST)

        if form.is_valid():
            # Separate receivers by comma, add to list
            for key, value in form.cleaned_data.items():
                if key == 'multiple_receivers':
                    receivers = list(map(str, value.split(';')))

            # Sends a message to users that exists in database
            for name in receivers:
                if (User.objects.filter(username=name).exists()):
                    to_user = User.objects.get(username=name)
                    form_msg = form.save(commit=False)
                    new_msg = Message.objects.create(
                        sender=request.user, 
                        receiver=to_user,
                        msg_title=form_msg.msg_title, 
                        msg_content=form_msg.msg_content,
                        multiple_receivers=form_msg.multiple_receivers,
                    )
                    new_msg.save()
                else:
                    raise Http404
            message = "200"
            return HttpResponse(json.dumps({'message': message}))
        else:
            message = "Something went wrong, try again."
            return HttpResponse(json.dumps({'message': message}))
         
    return redirect('/inbox')

# Sets message 'deleted' field to True.
def delete_message(request, id):
    message = get_object_or_404(Message, pk=id)

    if (request.is_ajax and request.method == 'POST'):
        message.deleted = True
        message.save()
        return JsonResponse({"success": True}, status = 200)
    else:
        html = "<html><body>Could not delete %s.</body></html>"
        return HttpResponse(html)

def undelete_message(request, id):
    message = get_object_or_404(Message, pk=id)
    if (request.is_ajax and request.method == 'POST'):
        if (message.deleted == True):
            message.deleted = False
        message.save()
        return JsonResponse({"success": True}, status = 200)
    else:
        html = "<html><body>Could not delete.</body></html>"
        return HttpResponse(html)