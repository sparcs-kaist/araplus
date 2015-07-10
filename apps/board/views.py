
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse
from apps.board.models import *
import datetime
import json
# Create your views here.


@login_required(login_url='/session/login')
def post_write(request):
    post = {}
    post["new"] = True
    error = ""

    if request.method == 'POST':
        _User = request.user
        _UserProfile = _User.userprofile
        board = request.POST.get('board', '')
        post["title"] = request.POST.get('title', '')
        post["content"] = request.POST.get('content', '')
        anonymous = request.POST.get('anonymous', '')
        adult = request.POST.get('adult', '')
        if post["title"] == '':
            error = 'title missing!'
        if post["content"] == '':
            error = 'content missing!'
        if error:
            return render(request,
                          'board/board_write.html',
                          {"error": error, "post": post})
        _BoardContent = BoardContent()
        _BoardContent.content = post["content"]
        _BoardContent.created_time = datetime.datetime.today()
        if anonymous == 'on':
            _BoardContent.is_anonymous = True
        if adult == 'on':
            _BoardContent.is_adult = True
        _BoardContent.save()
        _BoardPost = BoardPost()
        _BoardPost.title = post["title"]
        _BoardPost.board_content = _BoardContent
        _BoardPost.board_content_id = _BoardContent.id
        _BoardPost.author = _UserProfile
        _BoardPost.author_id = _UserProfile.id
        _Board = Board.objects.filter(id=board)
        if _Board:
            _BoardPost.board = _Board[0]
        else:
            return redirect('../')
        _BoardPost.save()
        return redirect('../%d/' % _BoardPost.id)
    cur_board = request.GET.get("board")
    Cur_board = Board.objects.filter(id=cur_board)[0]
    _Board = Board.objects.all()
    boards = []
    for bd in _Board:
        board = {}
        board['name'] = bd.name
        board['id'] = bd.id
        board['description'] = bd.description
        boards.append(board)
    return render(request,
                  'board/board_write.html',
                  {"post": post, "Boards": boards, "Cur_board": Cur_board})


@login_required(login_url='/session/login')
def post_read(request, pid, error=''):
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
    else:
        error = "No post"
        return render(request, 'board/board_read.html', {'error': error})
    _BoardContent = _BoardPost.board_content
    _UserProfile = _BoardPost.author
    _User = _UserProfile.user
    post = {}
    if _BoardContent.is_deleted:
        post["title"] = "--Deleted--"
        post["content"] = "--Deleted--"
        post["deleted"] = True
    else:
        post["title"] = _BoardPost.title
        post["content"] = _BoardContent.content
        post["deleted"] = False
    post["content_id"] = _BoardContent.id
    post["created_time"] = _BoardContent.created_time
    post["username"] = _User.username
    post["board"] = _BoardPost.board.name
    if _BoardContent.is_anonymous:
        post["username"] = 'anonymous'
    writing_id = _UserProfile.id
    reading_id = request.user.userprofile.id
    post["return"] = (writing_id == reading_id)
    post["vote"] = _BoardContent.get_vote()
    post["adult"] = _BoardContent.is_adult
    comments = []
    for cm in _BoardPost.comment.all():
        _BoardContent = cm.board_content
        _UserProfile = cm.author
        _User = _UserProfile.user
        comment = {}
        comment["username"] = _User.username
        if _BoardContent.is_deleted:
            comment["title"] = "--Deleted--"
            comment["content"] = "--Deleted--"
            comment["deleted"] = True
        else:
            comment["title"] = _BoardPost.title
            comment["content"] = _BoardContent.content
            comment["deleted"] = False
        comment["comment_id"] = cm.id
        comment["content_id"] = _BoardContent.id
        comment["created_time"] = _BoardContent.created_time
        comment["return"] = (_UserProfile.id
                             == request.user.userprofile.id)
        if _BoardContent.is_anonymous:
            comment["username"] = 'anonymous'
        comment["return"] = (_UserProfile.id == reading_id)
        comment["vote"] = _BoardContent.get_vote()
        comments.append(comment)
    return render(request,
                  'board/board_read.html',
                  {'error': error, 'post': post, 'comments': comments})


@login_required(login_url='/session/login')
def post_modify(request, pid):
    post = {}
    post["new"] = False
    error = ""
    _User = request.user
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
        if _BoardPost.author_id != _User.id:
            error = "Not allowed"
    else:
        error = "No post"
    _BoardContent = _BoardPost.board_content
    if _BoardContent.is_deleted:
        error = "Deleted"
    if error:
        return redirect('../')
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return redirect('session/login')
        _User = request.user
        post["title"] = request.POST.get('title', '')
        post["content"] = request.POST.get('content', '')
        adult = request.POST.get('adult', '')
        if post["title"] == '':
            error = 'title missing!'
        if post["content"] == '':
            error = 'body missing!'
        if error:
            return render(request,
                          'board/board_write.html',
                          {"error": error, "post": post})
        if adult:
            _BoardContent.is_adult = True
        else:
            _BoardContent.is_adult = False
        _BoardContent.content = post["content"]
        _BoardContent.save()
        _BoardPost.title = post["title"]
        _BoardPost.save()
        return redirect('../')
    post["title"] = _BoardPost.title
    post["content"] = _BoardContent.content
    return render(request,
                  'board/board_write.html',
                  {"post": post})


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

        content = request.POST.get('content', '')
        anonymous = request.POST.get('anonymous', '')
        if content == '':
            error = 'content missing!'
        if error:
            return redirect('../')
        _BoardContent = BoardContent()
        _BoardContent.content = content
        _BoardContent.created_time = datetime.datetime.today()
        if anonymous == 'on':
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
        cid = request.POST.get('cid', '')
        _BoardComment = BoardComment.objects.filter(id=cid)
        if _BoardComment:
            _BoardComment = _BoardComment[0]
            if _BoardComment.author_id != _User.id:
                error = "Not allowd"
        else:
            error = "No Comment"
        if error:
            return redirect('../')
        _BoardContent = _BoardComment.board_content
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
    adult_filter = request.GET.get('adult_filter')
    board_filter = request.GET.get('board')
    cur_board = ""
    is_adult = False
    if adult_filter == "true":
        is_adult = True
    if board_filter:
        _BoardPost= BoardPost.objects.filter(board=board_filter).order_by('-id')
        cur_board = Board.objects.filter(id=board_filter)[0]
    else:
        _BoardPost = BoardPost.objects.all().order_by('-id')
    

    _Board = Board.objects.all()
    paginator=Paginator(_BoardPost,10)
    try:
        page=int(request.GET['page'])
    except:
        page=1
    _PageBoardPost=paginator.page(page)
    posts = []
    boards = []
    for bd in _Board:
        boards.append(bd)
    for bp in _PageBoardPost:
        post = {}
        if bp.board_content.is_anonymous:
            post['username'] = "annonymous"
        else:
            post['username'] = bp.author.user.username
        post['board'] = bp.board.name
        if bp.board_content.is_deleted:
            post['title'] = "--Deleted--"
        else:
            post['title'] = bp.title
        post['created_time'] = bp.board_content.created_time
        post['id'] = bp.id
        post['board_id']=bp.board.id
        vote = bp.board_content.get_vote()
        post['up'] = vote['up']
        post['down'] = vote['down']
        if adult_filter == 'true' and bp.board_content.is_adult:
            post['title'] = "filterd"
        posts.append(post)
    if page==1:
        prevPage=0
    else:
        prevPage= paginator.page(page).previous_page_number()
    if page==paginator.num_pages:
        nextPage=page
    else:
        nextPage= paginator.page(page).next_page_number()
    return render(request,
                  'board/board_list.html',
                  {
                      'Posts': posts,
                      'Boards': boards,
                      'Cur_board': cur_board,
                      'Is_adult': is_adult,
                      'show_paginator':paginator.num_pages>1,
                      'has_prev':paginator.page(page).has_previous(),
                      'has_next':paginator.page(page).has_next(),
                      'page':page,
                      'pages':paginator.num_pages,
                      'next_page':nextPage,
                      'prev_page':prevPage,

                  })


@login_required(login_url='/session/login')
def up(request):
    message = ""
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)
    if _BoardContent:
        _BoardContent = _BoardContent[0]
        _BoardContentVote = BoardContentVote.objects.filter(
            board_content=_BoardContent,
            userprofile=request.user.userprofile)
        if _BoardContentVote:
            vote = _BoardContentVote[0]
            if vote.is_up:
                vote.delete()
                message = "success_up_cancle"
            else:
                vote.is_up = True
                vote.save()
                message = "success_up"
        else:
            vote = BoardContentVote()
            vote.is_up = True
            vote.userprofile = request.user.userprofile
            vote.board_content = _BoardContent
            vote.save()
            message = "success_up"
    else:
        message = "fail"
    result = {}
    result['message'] = message
    result['vote'] = _BoardContent.get_vote()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/session/login')
def down(request):
    message = ""
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)
    if _BoardContent:
        _BoardContent = _BoardContent[0]
        _BoardContentVote = BoardContentVote.objects.filter(
            board_content=_BoardContent,
            userprofile=request.user.userprofile)
        if _BoardContentVote:
            vote = _BoardContentVote[0]
            if not vote.is_up:
                vote.delete()
                message = "success_down_cancle"
            else:
                vote.is_up = False
                vote.save()
                message = "success_down"
        else:
            vote = BoardContentVote()
            vote.is_up = False
            vote.userprofile = request.user.userprofile
            vote.board_content = _BoardContent
            vote.save()
            message = "success_down"
    else:
        message = "fail"
    result = {}
    result['message'] = message
    result['vote'] = _BoardContent.get_vote()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/session/login')
def vote_adult(request):
    message = ""
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)
    if _BoardContent:
        _BoardContent = _BoardContent[0]
        _BoardContentVoteAdult = BoardContentVoteAdult.objects.filter(
            board_content=_BoardContent,
            userprofile=request.user.userprofile)
        if _BoardContentVoteAdult:
            message = "already voted_adult"
        else:
            vote = BoardContentVoteAdult()
            vote.userprofile = request.user.userprofile
            vote.board_content = _BoardContent
            vote.save()
            message = "success"
    else:
        message = "content not exist"
    result = {}
    result['message'] = message
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/session/login')
def vote_political(request):
    message = ""
    id = request.GET.get('id')
    _BoardContent = BoardContent.objects.filter(id=id)
    if _BoardContent:
        _BoardContent = _BoardContent[0]
        _BoardContentVotePolitical = BoardContentVotePolitical.objects.filter(
            board_content=_BoardContent,
            userprofile=request.user.userprofile)
        if _BoardContentVotePolitical:
            message = "already voted_political"
        else:
            vote = BoardContentVotePolitical()
            vote.userprofile = request.user.userprofile
            vote.board_content = _BoardContent
            vote.save()
            message = "success"
    else:
        message = "content not exist"
    result = {}
    result['message'] = message
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/session/login')
def delete(request):
    message = ""
    cid = request.GET.get('id')
    _BoardContents = BoardContent.objects.filter(id=cid)
    if _BoardContents:
        BoardCont = _BoardContents[0]
        if hasattr(BoardCont, 'boardpost'):
            author = BoardCont.boardpost.author
        elif hasattr(BoardCont, 'comment'):
            author = BoardCont.comment.author
        else:
            message = "no post or comment"
            return HttpResponse(message)
        if author == request.user.userprofile:
            BoardCont.is_deleted = True
            BoardCont.save()
            message = "success"
        else:
            message = "not allowed"
    else:
        message = "no content"
    return HttpResponse(message)
