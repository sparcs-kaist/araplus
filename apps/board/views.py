from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from apps.board.models import *
import datetime
# Create your views here.


@login_required(login_url='/session/login')
def board_write(request, error=''):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return redirect('session/login')
        _User = request.user
        _UserProfile = _User.userprofile

        title = request.POST.get('title','')
        content = request.POST.get('content','')
        anonymous = request.POST.get('anonymous','')
        if title == '':
            error = 'title missing!'
        if content == '':
            error = 'body missing!'
        if error:
            return render(request, 'board/board_write.html', {'error':error,'title':title,'content':content})
        _BoardContent = BoardContent()
        _BoardContent.content = content
        _BoardContent.created_time = datetime.datetime.today()
        if anonymous=='on':
            _BoardContent.is_anonymous = True
        _BoardContent.save()
        _BoardPost = BoardPost()
        _BoardPost.title = title
        _BoardPost.board_content = _BoardContent
        _BoardPost.board_content_id = _BoardContent.id
        _BoardPost.author = _UserProfile
        _BoardPost.author_id = _UserProfile.id
        _BoardPost.save()
        return redirect('../%d/' %_BoardPost.id)
    return render(request, 'board/board_write.html')

@login_required(login_url='/session/login')
def board_read(request, id, error=''):
    _BoardPost = BoardPost.objects.filter(id=id)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        error = "No post"
        return render(request, 'board/board_read.html', {'error':error})
    _BoardContent = _BoardPost.board_content
    _UserProfile = _BoardPost.author
    _User = _UserProfile.user
    username = _User.username
    title = _BoardPost.title
    content = _BoardContent.content
    created_time = _BoardContent.created_time
    if _BoardContent.is_anonymous:
        username = 'anonymous'
    return render(request, 'board/board_read.html', {'error':error,'id':id,'username':username,'title':title,'content':content,'created_time':created_time})

@login_required(login_url='/session/login')
def board_modify(request, id, error=''):
    _User = request.user
    _BoardPost = BoardPost.objects.filter(id=id)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        error = "No post"
    if _BoardPost.author_id != _User.id:
        error = "Not allowed"
    if error:
        return redirect('../')
    _BoardContent = _BoardPost.board_content
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return redirect('session/login')
        _User = request.user
        _UserProfile = _User.userprofile

        title = request.POST.get('title','')
        content = request.POST.get('content','')
        if title == '':
            error = 'title missing!'
        if content == '':
            error = 'body missing!'
        if error:
            return render(request, 'board/board_write.html', {'error':error,'title':title,'content':content})
        _BoardContent.content = content
        _BoardContent.save()
        _BoardPost.title = title
        _BoardPost.save()
        return redirect('../')
    title = _BoardPost.title
    content = _BoardContent.content
    return render(request, 'board/board_write.html', {'title':title,'content':content})
