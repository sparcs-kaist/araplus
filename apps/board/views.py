from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from apps.board.models import *
import datetime
# Create your views here.


# @login_required(login_url='/session/login')
def board_write(request):
    if request.method == 'POST':
        # if not request.user.is_authenticated():
            # return redirect('session/login')
        title = request.POST.get('title','')
        body = request.POST.get('body','')
        if title == '':
            error = 'title missing!'
            return render(request, 'board/board_write.html', {'error':error})
        if body == '':
            error = 'body missing!'
            return render(request, 'board/board_write.html', {'error':error})
        _BoardContent = BoardContent()
        _BoardContent.content = body
        _BoardContent.created_time = datetime.datetime.today()
        _BoardContent.save()
        _BoardPost = BoardPost()
        _BoardPost.title = title
        _BoardPost.board_content = _BoardContent
        _BoardPost.board_content_id = _BoardContent.id
        _BoardPost.save()
        return redirect('../%d/' %_BoardPost.id)
    return render(request, 'board/board_write.html')

def board_read(request, id):
    _BoardPost = BoardPost.objects.filter(id=id)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        render(request, 'board/board_read.html', {'error':error})
    _BoardContent = _BoardPost.board_content
    title = _BoardPost.title
    content = _BoardContent.content
    return render(request, 'board/board_read.html', {'id':id,'title':title,'content':content})
