# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.board.models import *
from apps.board.backend import _get_post_list, _get_board_list
from apps.board.backend import _get_querystring, _get_content
from apps.board.backend import _write_post, _get_current_board
from apps.board.backend import _delete_post, _report, _vote
from django.utils import timezone
import json


def home(request):
    return redirect('all/')


@login_required(login_url='/session/login')
def post_write(request, board_url):
    post = {}
    post['new'] = True
    if request.method == 'POST':
        post_id = _write_post(request, 'Post')
        if post_id:
            #  board_id = BoardPost.objects.filter(id=post_id)[0].board.id
            return redirect('../' + str(post_id))
        else:
            return redirect('../')
    current_board = _get_current_board(request, board_url)
    # official=request.user.userprofile.is_official
    board_list = _get_board_list()
    categories = BoardCategory.objects.all()
    return render(request,
                  'board/board_write.html',
                  {"post": post, "board_list": board_list,
                   "current_board": current_board,
                   "Categories": categories})


@login_required(login_url='/session/login')
def post_read(request, board_url, post_id):
    get_content = _get_content(request, post_id)
    post = get_content[0]
    comment_list = get_content[1]
    get_post_list = _get_post_list(request, board_url)
    post_list = get_post_list[0]
    paginator = get_post_list[1]
    board_list = _get_board_list()
    querystring = _get_querystring(request, 'best', 'page')
    current_board = _get_current_board(request, board_url)
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
def post_modify(request, board_url, post_id):
    try:
        board_post = BoardPost.objects.filter(id=post_id)[0]
        if request.user.userprofile != board_post.author:
            return
    except:
        return
    if request.method == 'POST':
        post_id = _write_post(request, 'Post', modify=True)
        if post_id:
            querystring = _get_querystring(request, 'best', 'page')
            return redirect('../'+querystring)
        return redirect('../')
    post = _get_content(request, post_id)[0]
    post['new'] = False
    current_board = _get_current_board(request, board_url)
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
    querystring = _get_querystring(request, 'bset', 'page')
    return redirect('../'+querystring)


@login_required(login_url='/session/login')
def comment_modify(request, post_id_check):
    if request.method == 'POST':
        post_id = _write_post(request, 'Comment', post_id_check, True)
    querystring = _get_querystring(request, 'best', 'page')
    return redirect('../'+querystring)


@login_required(login_url='/session/login')
def re_comment_write(request):
    if request.method == 'POST':
        post_id = _write_post(request, 'Re-Comment')
    querystring = _get_querystring(request, 'best', 'page')
    return redirect('../'+querystring)


@login_required(login_url='/session/login')
def post_list(request, board_url):
    get_post_list = _get_post_list(request, board_url)
    post_list = get_post_list[0]
    paginator = get_post_list[1]
    board_list = _get_board_list()
    querystring = _get_querystring(request, 'best', 'page')
    current_board = _get_current_board(request, board_url)
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
def content_vote(request):
    result = {}
    result['response'] = 'fail'
    if request.method == 'POST':
        vote_result = _vote(request)
        if 'success' in vote_result:
            result['response'] = 'success'
            result['message'] = vote_result['success']
            result['vote'] = vote_result['vote']
            result['cancel'] = vote_result['cancel']
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required(login_url='/session/login')
def delete(request):
    message = 'invalid access'
    if request.method == 'POST':
        message = _delete_post(request)
    return HttpResponse(message)


@login_required(login_url='/session/login')
def report(request):
    message = 'invalid access'
    if request.method == 'POST':
        message = _report(request)
    return HttpResponse(message)
