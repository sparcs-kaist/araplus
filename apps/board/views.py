# -*- coding: utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.board.models import *
from apps.board.backend import (
    _get_post_list,
    _get_querystring,
    _get_content,
    _write_post,
    _delete_post,
    _report,
    _vote,
    _write_comment,
    _create_board,
)
from itertools import izip
import json
import diff_match_patch
from apps.board.forms import *


def home(request):
    return redirect('all/')


@login_required(login_url='/session/login')
def create_board(request):
    if request.method == 'POST':
        result = _create_board(request)
        if 'save' in result:
            return redirect('../' + result['save'].url + '/')
        else:
            form_board = result['failed']
    else:
        form_board = BoardForm()
    return render(request,
                  'board/create_board.html',
                  {'board_form' : form_board})


@login_required(login_url='/session/login')
def post_write(request, board="All"):
    if request.method == 'POST':
        result = _write_post(request, board=board)
        if 'save' in result:
            board_post_trace = BoardPostTrace(
                board_post=result['save'],
                userprofile=request.user.userprofile)
            board_post_trace.save()
            return redirect('../' + str(result['save'].id) + '/')
        else:
            form_content, form_post = result['failed']
    else:
        try:
            board = Board.objects.get(url=board)
        except:
            board = Board.objects.get(id=1)
        form_content = BoardContentForm()
        form_post = BoardPostForm(initial={'board': board.id})
    return render(request,
                  'board/board_write.html',
                  {'content_form': form_content,
                   'post_form': form_post})


@login_required(login_url='/session/login')
def post_modify(request, post_id=0):
    post_instance = get_object_or_404(BoardPost, id=post_id)
    if post_instance.author != request.user.userprofile:
        return redirect('../')
    if request.method == "POST":
        result = _write_post(request, True, post_instance,
                             post_instance.board_content)
        if 'save' in result:  # success modify
            return redirect('../')
        else:
            form_content, form_post = result['failed']
    else:
        form_content = BoardContentForm(
            is_modify=True,
            instance=post_instance.board_content)
        form_post = BoardPostForm(is_modify=True, instance=post_instance)
    return render(request,
                  'board/board_write.html',
                  {'content_form': form_content,
                   'post_form': form_post})


@login_required(login_url='/session/login')
def post_read(request, board_url, post_id):
    post, comment_list = _get_content(request, post_id)
    notice_list, post_list, pages, page = _get_post_list(request, board_url)
    board_list = Board.objects.all()
    try:
        board_post_trace = BoardPostTrace.objects.get(
            userprofile=request.user.userprofile,
            board_post__id=post_id)
    except:
        board_post_trace = None
    try:
        current_board = board_list.get(url=board_url)
        print current_board
    except:
        current_board = None
    querystring = _get_querystring(request, 'best', 'page')
    # tested for report ########
    report_form = BoardReportForm()
    """return render(request,
                  'board/modal_test.html',
                  {'report_form': report_form})"""
    #################################
    return render(request,
                  'board/board_read.html',
                  {
                      'querystring': querystring,
                      'post': post,  # post for post
                      'comment_list': comment_list,  # comment for post
                      'board_post_trace': board_post_trace,
                      # Below,there are thing for postList.
                      'notice_list': notice_list,
                      'post_list': post_list,
                      'pages': pages,
                      'current_page': page,
                      'board_list': board_list,
                      'current_board': current_board,
                      'report_form': report_form
                  })


@login_required(login_url='/session/login')
def post_modify_log(request, board_url, post_id):
    diff_obj = diff_match_patch.diff_match_patch()
    board_post = BoardPost.objects.filter(id=post_id)[0]
    board_content = board_post.board_content
    post = [board_post.title,
            board_post.board.kor_name,
            board_post.board_category,
            board_content.modified_time,
            board_content.content]
    modify_log = []
    for log_post, log_content in izip(board_post.get_log(),
                                      board_post.board_content.get_log()):
        modify_log = modify_log +\
            [[diff_obj.diff_prettyHtml(log_post[0]),
              diff_obj.diff_prettyHtml(log_post[1]),
              diff_obj.diff_prettyHtml(log_post[2]),
              log_content[0],
              diff_obj.diff_prettyHtml(log_content[1])]]
    return render(request, "board/log.html",
                  {
                      'post': post,
                      'modify_log': modify_log,
                  })


@login_required(login_url='/session/login')
def comment_write(request, post_id):
    if request.method == 'POST':
        post_id = _write_comment(request, post_id)
    querystring = _get_querystring(request, 'bset', 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def comment_modify(request, post_id):
    if request.method == 'POST':
        post_id = _write_comment(request, post_id, True)
    querystring = _get_querystring(request, 'best', 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def post_list(request, board_url):
    notice_list, post_list, pages, page = _get_post_list(request, board_url)
    board_list = Board.objects.filter(is_official=True)
    try:
        current_board = Board.objects.get(url=board_url)
    except:
        current_board = None
    querystring = _get_querystring(request, 'best', 'page')
    return render(request,
                  'board/board_list.html',
                  {'notice_list':  notice_list,
                   'post_list': post_list,
                   'board_list': board_list,
                   'current_board': current_board,
                   'pages': pages,
                   'current_page': page,
                   'querystring': querystring})


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
    if request.method == 'POST':
        message = _report(request)
    return HttpResponse(json.dumps(message), content_type='application/json')


@login_required(login_url='/session/login')
def trace(request, post_id):
    message = 'fail'
    if request.method == 'POST':
        try:
            board_post_trace = BoardPostTrace.objects.get(
                userprofile=request.user.userprofile,
                board_post__id=post_id)
            board_post_trace.is_trace = not(board_post_trace.is_trace)
            print board_post_trace.is_trace
            board_post_trace.save()
            message = 'success'
        except:
            message = 'no post'
    return HttpResponse(message)
