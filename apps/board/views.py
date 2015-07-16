# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse
from apps.board.models import *
import datetime
import json

ItemPerPage=15

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
        category = request.POST.get('category', '')
        anonymous = request.POST.get('anonymous', '')
        adult = request.POST.get('adult', '')
        notice = request.POST.get('notice', '')
        if post["title"] == '':
            error = 'title missing!'
        if post["content"] == '':
            error = 'content missing!'
        if error:
            Cur_board = Board.objects.filter(id=board)[0]
            _Board = Board.objects.all()
            # official=request.user.userprofile.is_official
            boards = []
            for bd in _Board:
                board = {}
                board['name'] = bd.name
                board['id'] = bd.id
                board['description'] = bd.description
                boards.append(board)
            categories = BoardCategory.objects.all()
            return render(request,
                          'board/board_write.html',
                          {"post": post, "Boards": boards,
                           "Cur_board": Cur_board, "error": error,
                           "Categories": categories})
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
        if notice == 'on':
            _BoardPost.is_notice = True
        _BoardPost.board_content = _BoardContent
        _BoardPost.board_content_id = _BoardContent.id
        _BoardPost.author = _UserProfile
        _BoardPost.author_id = _UserProfile.id
        _Board = Board.objects.filter(id=board)
        if _Board:
            _BoardPost.board = _Board[0]
        else:
            return redirect('../')
        _Category = BoardCategory.objects.filter(name=category)
        if _Category:
            _BoardPost.board_category = _Category[0]
        else:
            return redirect('../')
        _BoardPost.save()
        postID = str(_BoardPost.id)
        return redirect('../'+postID+'/?board='+board)
    cur_board = request.GET.get("board")
    if cur_board:
        Cur_board = Board.objects.filter(id=cur_board)[0]
    else:
        Cur_board = Board.objects.filter(id=1)[0]
    _Board = Board.objects.all()
    # official=request.user.userprofile.is_official
    boards = []
    for bd in _Board:
        board = {}
        board['name'] = bd.name
        board['id'] = bd.id
        board['description'] = bd.description
        boards.append(board)
    categories = BoardCategory.objects.all()
    return render(request,
                  'board/board_write.html',
                  {"post": post, "Boards": boards,
                   "Cur_board": Cur_board,
                   "Categories": categories})

            
@login_required(login_url='/session/login')
def post_read(request, pid, error=''):
    post_list = _get_post_list(request)[0]
    paginator = _get_post_list(reauest)[1]
    board_list = _get_baord_list()
    querysting = _get_querystring(request)
    board = _get_board_current(request)
    adult_filter = request.GET.get('adult_filter')
    is_adult = False
    if adult_filter == "true":
        is_adult = True
    post  = _get_content(request)[0]
    comment_list = _get_content(request)[1]
 
    return render(request,
                  'board/board_read.html',
                  {
                      'querystring' : querystring,
                      'post' : post,  # post for post
                      'comment_list' : comment_list,  # comment for post  
                      # Below,there are thing for postList.
                      'post_list' : post_list,
                      'board_list': board_list,
                      'board' : board,
                      'is_adult' : is_adult,
                      'paginator' : paginator, 
                  })


@login_required(login_url='/session/login')
def post_modify(request, pid):
    post = {}
    post["new"] = False
    error = ""
    _User = request.user
    _BoardPost = BoardPost.objects.filter(id=pid)
    if _BoardPost:
        _BoardPost = _BoardPost[0]
        if _BoardPost.author != _User.userprofile:
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
        post["board"] = request.POST.get('board', '')
        post["category"] = request.POST.get('category', '')
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
        _Board = Board.objects.filter(id=post["board"])
        _Category = BoardCategory.objects.filter(name=post["category"])
        if not _Board:
            return redirect('../')
        elif not _Category:
            return redirect('../')
        else:
            _BoardPost.board = _Board[0]
            _BoardPost.board_category = _Category[0]
        _BoardPost.save()
        return redirect('../')
    post["title"] = _BoardPost.title
    post["content"] = _BoardContent.content
    cur_board = request.GET.get("board", '')
    if cur_board:
        Cur_board = Board.objects.filter(id=cur_board)[0]
    else:
        Cur_board = Board.objects.filter(id=1)[0]
    _Board = Board.objects.all()
    # official=request.user.userprofile.is_official
    boards = []
    for bd in _Board:
        board = {}
        board['name'] = bd.name
        board['id'] = bd.id
        board['description'] = bd.description
        boards.append(board)
    categories = BoardCategory.objects.all()
    return render(request,
                  'board/board_write.html',
                  {"post": post, "Boards": boards,
                   "Cur_board": Cur_board,
                   "Categories": categories})

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
            if _BoardComment.author != _User.userprofile:
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
    post_list = _get_post_list(request)[0]
    paginator = _get_post_list(reauest)[1]
    board_list = _get_baord_list()
    querysting = _get_querystring(request)
    board = _get_board_current(request)
    adult_filter = request.GET.get('adult_filter')
    is_adult = False
    if adult_filter == "true":
        is_adult = True

    return render(request,
                  'board/board_list.html',
                  {
                      'post_list' : post_list,
                      'board_list' : board_list,
                      'board' : board,
                      'is_adult' : is_adult,
                      'querystirng' : querystring,
                      'paginator' : paginator,

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


@login_required(login_url='/session/login')
def report(request):
    if request.method == 'POST':
        cid = request.POST.get('id', '')
        reason = request.POST.get('report_reason', '')
        content = request.POST.get('report_content', '')
        if reason == '' or reason == '0':
            message = 'no reason'
        else:
            board_content = BoardContent.objects.filter(id=cid)
            if board_content:
                board_content = board_content[0]
                board_report = BoardReport()
                board_report.reason = reason
                board_report.content = content
                board_report.board_content = board_content
                board_report.created_time = datetime.datetime.today()
                board_report.userprofile = request.user.userprofile
                board_report.save()
                message = 'success'
            else:
                message = 'no content'
        return HttpResponse(message)
