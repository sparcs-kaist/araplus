# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.board.models import *
from apps.board.backend import _get_post_list, _get_board_list
from apps.board.backend import _get_querystring, _get_content
from apps.board.backend import _write_post, _get_current_board
from django.utils import timezone
import json


@login_required(login_url='/session/login')
def post_write(request):
    post = {}
    post['new'] = True
    if request.method == 'POST':
        post_id = _write_post(request, 'Post')
        if post_id:
            querystring = _get_querystring(request)
            #  board_id = BoardPost.objects.filter(id=post_id)[0].board.id
            return redirect('../' + str(post_id) + querystring)
        else:
            return redirect('../')
    current_board = _get_current_board(request)
    # official=request.user.userprofile.is_official
    board_list = _get_board_list
    categories = BoardCategory.objects.all()
    return render(request,
                  'board/board_write.html',
                  {"post": post, "board_list": board_list,
                   "current_board": current_board,
                   "Categories": categories})


@login_required(login_url='/session/login')
def post_read(request, post_id):
    get_post_list = _get_post_list(request)
    post_list = get_post_list[0]
    paginator = get_post_list[1]
    board_list = _get_board_list()
    querystring = _get_querystring(request)
    current_board = _get_current_board(request)
    get_content = _get_content(request, post_id)
    post = get_content[0]
    comment_list = get_content[1]
    return render(request,
                  'board/board_read.html',
                  {
                      'querystring': querystring,
                      'post': post,  # post for post
                      'comment_list': comment_list,  # comment for post
                      # Below,there are thing for postList.
                      'post_list': post_list,
                      'board_list': board_list,
                      'current_board': current_board,
                      'paginator': paginator,
                  })


@login_required(login_url='/session/login')
def post_modify(request, post_id):
    try:
        board_post = BoardPost.objects.filter(id=post_id)[0]
        if request.user.userprofile != board_post.author:
            return
    except:
        return
    if request.method == 'POST':
        post_id = _write_post(request, 'Post', modify=True)
        if post_id:
            querystring = _get_querystring(request)
            return redirect('../'+querystring)
        return redirect('../')
    post = _get_content(request, post_id)[0]
    post['new'] = False
    current_board = _get_current_board(request)
    board_list = _get_board_list()
    # official=request.user.userprofile.is_official
    categories = BoardCategory.objects.all()
    return render(request,
                  'board/board_write.html',
                  {"post": post, "board_list": board_list,
                   "current_board": current_board,
                   "Categories": categories})


@login_required(login_url='/session/login')
def comment_write(request, post_id_check):
    if request.method == 'POST':
        post_id = _write_post(request, 'Comment', post_id_check)
    return redirect('../')


@login_required(login_url='/session/login')
def comment_modify(request, post_id_check):
    if request.method == 'POST':
        post_id = _write_post(request, 'Comment', post_id_check, True)
    return redirect('../')


@login_required(login_url='/session/login')
def re_comment_write(request):
    if request.method == 'POST':
        post_id = _write_post(request, 'Re-Comment')
    return redirect('../')


@login_required(login_url='/session/login')
def post_list(request):
    get_post_list = _get_post_list(request)
    post_list = get_post_list[0]
    paginator = get_post_list[1]
    board_list = _get_board_list()
    querystring = _get_querystring(request)
    current_board = _get_current_board(request)
    adult_filter = request.GET.get('adult_filter')
    is_adult = False
    if adult_filter == "true":
        is_adult = True
    return render(request,
                  'board/board_list.html',
                  {
                      'post_list': post_list,
                      'board_list': board_list,
                      'current_board': current_board,
                      'is_adult': is_adult,
                      'querystring': querystring,
                      'paginator': paginator,
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
                board_report.created_time = timezone.now()
                board_report.userprofile = request.user.userprofile
                board_report.save()
                message = 'success'
            else:
                message = 'no content'
        return HttpResponse(message)
