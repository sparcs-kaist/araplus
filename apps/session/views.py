from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from apps.session.models import UserProfile, Message
from django.contrib.auth.decorators import login_required
import re
import json
import urllib


# Session main page
def main(request):
    return render(request, 'session/main.html')


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
    if request.user.is_authenticated():
        return redirect('/')
    return redirect('https://sso.sparcs.org/oauth/require/?url=' + \
                    request.build_absolute_uri('/session/login/callback/'))


def user_login_callback(request):
    if request.method == "GET":
        nexturl = request.GET.get('next', '/')
        tokenid = request.GET['tokenid']
        sso_profile = urllib.urlopen('https://sso.sparcs.org/' + \
                                     'oauth/info?tokenid='+tokenid)
        sso_profile = json.load(sso_profile)
        username = sso_profile['sid']
        user_list = User.objects.filter(username=username)
        if len(user_list) == 0:
            request.session['info'] = sso_profile
            return redirect('/session/register')
        else:
            user_list[0].backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user_list[0])
            return redirect(nexturl)
    return render('/session/login.html', {'error': "Invalid login"})


def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/session/login/')


def user_register(request):
    if 'info' not in request.session:
        return redirect('/session/login/')

    info = request.session['info']
    if len(User.objects.filter(username=info['sid'])) > 0:
        del request.session['info']
        return redirect('/session/login/')

    if request.method == 'POST':
        nickname = request.POST['nickname']
        password = request.POST['password']
        if validate_nickname(nickname):
            user = User.objects.create_user(username=info['sid'],
                                            email=info['email'],
                                            password=password,
                                            first_name=info['first_name'],
                                            last_name=info['last_name'])

            user_profile = UserProfile(user=user,
                                       gender=info['gender'],
                                       # birthday=info['birthday'],
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


@login_required(login_url='/session/login/')
def view_notifications(request):
    user = request.user
    unread_noti = user.notifications.unread()
    read_noti = user.notifications.read()
    return render(request,
                  'session/notification_view.html',
                  {'unread': unread_noti, 'read': read_noti})
