from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from apps.session.models import UserProfile, Message
from django.contrib.auth.decorators import login_required
import re


def validate_nickname(nickname):
    if not re.match(r'[\w_-]{5,30}', nickname):
        return False

    user_profile = UserProfile.objects.filter(nickname=nickname)
    if len(user_profile) > 0:
        return False
    return True


def nickname_check(request):
    if validate_nickname(request.GET.get('nickname', '')):
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect(request.POST['next'])
        else:
            error = "Invalid login"
        return render(request, 'session/login.html', {'error': error})
    return render(request, 'session/login.html',
                  {'next': request.GET.get('next', '/')})


def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/session/login/')


def user_register(request):
    if 'info' not in request.session:
        return redirect('/session/login/')

    info = request.session['info']
    if len(User.objects.filter(username=info['username']) > 0):
        del request.session['info']
        return redirect('/session/login/')
    info = None
    if request.method == 'POST':
        nickname = request.POST['nickname']
        password = request.POST['password']
        if validate_nickname(nickname):
            user = User.objects.create_user(username=info['username'],
                                            email=info['email'],
                                            password=password,
                                            first_name=info['first_name'],
                                            last_name=info['last_name'])

            user_profile = UserProfile(user=user,
                                       gender=info['gender'],
                                       birthday=info['birthday'],
                                       nickname=nickname)
        user_profile.save()

        return render(request, 'session/register_complete.html')
    return render(request, 'session/register.html', {'info': info})


@login_required(login_url='/session/login/')
def send_message(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            sender = UserProfile.objects.get(user=request.user)
        else:
            error = "Login required"
            return render(request,
                          'session/write_message.html', {'error': error})
        content = request.POST['content']
        receiver = UserProfile.objects.get(nickname=request.POST['nickname'])
        new_message = Message(content=content,
                              sender=sender,
                              receiver=receiver,
                              is_read=False)
        new_message.save()

        return render(request, 'session/message_success.html')
    return render(request, 'session/write_message.html')


@login_required(login_url='/session/login/')
def check_message(request):
    if request.user.is_authenticated():
        sender = UserProfile.objects.get(user=request.user)
    else:
        error = "Login required"
        return render(request, 'session/check_message.html', {'error': error})
    messages = Message.objects.filter(receiver=sender)
    return render(request,
                  'session/check_message.html', {'messages': messages})
