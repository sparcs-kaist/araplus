from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from apps.board.models import *
import datetime
import json
# Create your views here.


@login_required(login_url='/session/login')
def post_write(request, error=''):
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
            error = 'content missing!'
        if error:
            return render(request, 'board/board_write.html', {'error':error,'new':True,'title':title,'content':content})
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
    return render(request, 'board/board_write.html', {'new':True,})

@login_required(login_url='/session/login')
def post_read(request, pid, error=''):
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        error = "No post"
        return render(request, 'board/board_read.html', {'error':error})
    _BoardContent = _BoardPost.board_content
    _UserProfile = _BoardPost.author
    _User = _UserProfile.user
    post = {}
    post["username"] = _User.username
    post["title"] = _BoardPost.title
    post["content"] = _BoardContent.content
    post["content_id"] = _BoardContent.id
    post["created_time"] = _BoardContent.created_time
    if _BoardContent.is_anonymous:
        post["username"] = 'anonymous'
    post["vote"] = _BoardContent.get_vote()
    comments = []
    for cm in _BoardPost.comment.all():
        _BoardContent = cm.board_content
        _UserProfile = cm.author
        _User = _UserProfile.user
        comment = {}
        comment["username"] = _User.username
        comment["title"] = _BoardPost.title
        comment["comment_id"] = cm.id
        comment["content"] = _BoardContent.content
        comment["content_id"] = _BoardContent.id
        comment["created_time"] = _BoardContent.created_time
        if _BoardContent.is_anonymous:
            comment["username"] = 'anonymous'
        comment["vote"] = _BoardContent.get_vote()
        comments.append(comment)
    return render(request, 'board/board_read.html', \
            {'error':error, 'post':post, 'comments':comments})

@login_required(login_url='/session/login')
def post_modify(request, pid, error=''):
    _User = request.user
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
        if _BoardPost.author_id != _User.id:
            error = "Not allowed"
    else:
        error = "No post"
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

@login_required(login_url='/session/login')
def comment_write(request, pid, error=''):
    _User = request.user
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        error = "No post"
    if error:
        return redirect('../')
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return redirect('session/login')
        _User = request.user
        _UserProfile = _User.userprofile

        content = request.POST.get('content','')
        anonymous = request.POST.get('anonymous','')
        if content == '':
            error = 'content missing!'
        if error:
            return redirect('../')
        _BoardContent = BoardContent()
        _BoardContent.content = content
        _BoardContent.created_time = datetime.datetime.today()
        if anonymous=='on':
            _BoardContent.is_anonymous = True
        _BoardContent.save()
        _BoardComment = BoardComment()
        _BoardComment.board_content = _BoardContent
        _BoardComment.board_post = _BoardPost
        _BoardComment.author = _UserProfile
        _BoardComment.save()
        return redirect('../')
    return redirect('../')


@login_required(login_url='/session/login')
def comment_modify(request, error=''):
    if request.method == "POST":
        _User = request.user
        cid = request.POST.get('cid','')
        _BoardComment = BoardComment.objects.filter(id = cid)
        if _BoardComment:
           _BoardComment = _BoardComment[0]
           if _BoardComment.author_id != _User.id:
               error = "Not allowd"
        else:
            error = "No Comment"
        if error:
            return redirect('../')
        _BoardContent = _BoardComment.board_content
        _UserProfie = _User.userprofile
        content = request.POST.get('content', '')
        if content == '':
            error = 'No comment content'
        if error:
            return redirect('../')
        _BoardContent.content = content
        _BoardContent.save()
        return redirect('../')
    error = "Invalid access"
    return redirect('../')

@login_required(login_url='/session/login')
def post_list(request, error=''):
    _BoardPost=BoardPost.objects.all()
    posts = []
    for bp in _BoardPost:
        post = {}
        if bp.board_content.is_anonymous:
            post['username']="annonymous"
        else:
            post['username']=bp.author.user.username
        post['board']="sdskjflsd"
        post['title']=bp.title
        post['created_time']=bp.board_content.created_time
        post['id']=bp.id
        up = 0
        down = 0
        for content_vote in bp.board_content.content_vote.all():
            if content_vote.is_up:
                up=up+1
            else:
               down= down+1

        post['up']=up
        post['down']=down
        posts.append(post)
    return render(request, 'board/board_list.html',{'Posts': posts})

@login_required(login_url='/session/login')
def up(request):
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)[0]
    _BoardContentVote=BoardContentVote.objects.filter(board_content=_BoardContent,userprofile=request.user.userprofile)
    message = ''
    if _BoardContentVote:
        vote = _BoardContentVote[0]
        if vote.is_up:
            message = "fail"
        else:
            vote.is_up = True
            vote.save()
            message = "success"
    else:
        vote = BoardContentVote()
        vote.is_up = True
        vote.userprofile = request.user.userprofile
        vote.board_content = BoardContent.objects.filter(id=id)[0]
        vote.save()
        message = "success"
    result = {}
    result['message'] = message
    result['vote'] = _BoardContent.get_vote()
    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required(login_url='/session/login')
def down(request):
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)[0]
    _BoardContentVote=BoardContentVote.objects.filter(board_content=_BoardContent,userprofile=request.user.userprofile)
    message = ''
    if _BoardContentVote:
        vote = _BoardContentVote[0]
        if not vote.is_up:
            message = "fail"
        else:
            vote.is_up = False
            vote.save()
            message = "success"
    else:
        vote = BoardContentVote()
        vote.is_up = False
        vote.userprofile = request.user.userprofile
        vote.board_content = BoardContent.objects.filter(id=id)[0]
        vote.save()
        message = "success"
    result = {}
    result['message'] = message
    result['vote'] = _BoardContent.get_vote()
    return HttpResponse(json.dumps(result), content_type="application/json")

