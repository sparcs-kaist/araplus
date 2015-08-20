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
    _get_post_log,
    _get_comment_log,
    _remove_board,
    _add_member,
    _check_valid,
)
import json
from apps.board.forms import *
from django.core.paginator import Paginator


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
                  {'board_form': form_board})


@login_required(login_url='/session/login')
def remove_board(request, board_url):
    return HttpResponse(_remove_board(request, board_url))


def add_member(request, board_url):
    try:
        board = Board.objects.get(url=board_url,
                                  admin=request.user.userprofile)
    except:
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        result = _add_member(request, board)
        if 'save' in result:
            return redirect('./')
        else:
            form_boardmember = result['failed']
    else:
        form_boardmember = BoardMemberForm()
    members = BoardMember.objects.filter(board=board)
    return render(request,
                  'board/add_member.html',
                  {'boardmember_form': form_boardmember, 'members': members})


def delete_member(request, board_url):
    try:
        board = Board.objects.get(url=board_url,
                                  admin=request.user.userprofile)
    except:
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        member_name = request.POST.get('member_name', '')
        try:
            member = BoardMember.objects.get(board=board,
                                             member__nickname=member_name)
            member.delete()
        except:
            pass
    return redirect('../')


@login_required(login_url='/session/login')
def post_write(request, board="All"):
    if not _check_valid(request, board, True):
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        result = _write_post(request, board=board)
        if 'save' in result:
            board_post_trace = BoardPostTrace(
                board_post=result['save'],
                userprofile=request.user.userprofile)
            board_post_trace.save()
            return redirect('../' + str(result['save'].id) + '/')
        else:
            form_content, form_post, form_attachment = result['failed']
    else:
        try:
            board = Board.objects.get(url=board)
        except:
            board = Board.objects.get(id=1)
        form_content = BoardContentForm()
        form_post = BoardPostForm(initial={'board': board.id})
        form_attachment = AttachmentFormSet(queryset=Attachment.objects.none())
    return render(request,
                  'board/board_write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment})


@login_required(login_url='/session/login')
def post_modify(request, board_url, post_id=0):
    if not _check_valid(request, board_url, True):
        return HttpResponse('Invalid access')
    post_instance = get_object_or_404(BoardPost, id=post_id)
    if post_instance.author != request.user.userprofile:
        return redirect('../')
    if request.method == "POST":
        result = _write_post(request, True, post_instance,
                             post_instance.board_content)
        if 'save' in result:  # success modify
            return redirect('../')
        else:
            form_content, form_post, form_attachment = result['failed']
    else:
        form_content = BoardContentForm(
            is_modify=True,
            instance=post_instance.board_content)
        form_post = BoardPostForm(is_modify=True, instance=post_instance)
        form_attachment = AttachmentFormSet(
            queryset=Attachment.objects.filter(
                board_content__board_post__id=post_id))
    return render(request,
                  'board/board_write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment})


@login_required(login_url='/session/login')
def post_read(request, board_url, post_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    post, comment_list = _get_content(request, post_id)
    notice_list, post_list, pages, page = _get_post_list(request, board_url)
    board_list = Board.objects.all()
    search_category = request.GET.get('category', '')
    try:
        board_post_trace = BoardPostTrace.objects.get(
            userprofile=request.user.userprofile,
            board_post__id=post_id)
    except:
        board_post_trace = None
    try:
        current_board = board_list.get(url=board_url)
    except:
        current_board = None
    try:
        current_category = BoardCategory.objects.get(name=search_category)
    except:
        current_category = None
    querystring = _get_querystring(request, 'best', 'page')
    report_form = BoardReportForm()
    attachment_form = AttachmentFormSet(queryset=Attachment.objects.none())
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
                      'report_form': report_form,
                      'current_category': current_category,
                      # Below thing is for attachment form for comment
                      'attachment_form': attachment_form
                  })


@login_required(login_url='/session/login')
def post_modify_log(request, board_url, post_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    post, modify_log = _get_post_log(post_id)
    return render(request, "board/post_log.html",
                  {
                      'post': post,
                      'modify_log': modify_log,
                  })


@login_required(login_url='/session/login')
def comment_modify_log(request, board_url, comment_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    comment, modify_log = _get_comment_log(comment_id)
    return render(request, "board/comment_log.html",
                  {
                      'comment': comment,
                      'modify_log': modify_log,
                  })


@login_required(login_url='/session/login')
def comment_write(request, board_url, post_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        post_id = _write_comment(request, post_id)
    querystring = _get_querystring(request, 'best', 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def comment_modify(request, board_url, post_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        post_id = _write_comment(request, post_id, True)
        print post_id
    querystring = _get_querystring(request, 'best', 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def post_list(request, board_url):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    notice_list, post_list, pages, page = _get_post_list(request, board_url)
    board_list = Board.objects.filter(is_official=True)
    try:
        current_board = Board.objects.get(url=board_url, is_deleted=False)
    except:
        current_board = None
    try:
        current_category = BoardCategory.objects.get(name=search_category)
    except:
        current_category = None
    querystring = _get_querystring(request, 'best', 'page')
    return render(request,
                  'board/board_list.html',
                  {'notice_list':  notice_list,
                   'post_list': post_list,
                   'board_list': board_list,
                   'current_board': current_board,
                   'pages': pages,
                   'current_page': page,
                   'querystring': querystring,
                   'current_category': current_category})


@login_required(login_url='/session/login')
def content_vote(request, board_url):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
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
def delete(request, board_url):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    message = 'invalid access'
    if request.method == 'POST':
        message = _delete_post(request)
    return HttpResponse(message)


@login_required(login_url='/session/login')
def report(request, board_url):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    if request.method == 'POST':
        message = _report(request)
    return HttpResponse(json.dumps(message), content_type='application/json')


@login_required(login_url='/session/login')
def trace(request, board_url, post_id):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    request_type = request.POST.get('type', '')
    try:
        board_post_trace = BoardPostTrace.objects.get(
            userprofile=request.user.userprofile,
            board_post__id=post_id)
        if request_type == 'trace':
            board_post_trace.is_trace = not(board_post_trace.is_trace)
        elif request_type == 'alarm':
            board_post_trace.is_notified = not(board_post_trace.is_notified)
        else:
            result = {'message': 'failed'}
            return HttpResponse(json.dumps(result),
                                content_type='application/json')
    except:
        board_post_trace = BoardPostTrace(
            userprofile=request.user.userprofile,
            board_post_id=post_id)
        if request_type == 'alarm':
            board_post_trace.is_notified = True
    board_post_trace.save()
    result = {
        'message': 'success',
        'alarm': board_post_trace.is_notified,
        'trace': board_post_trace.is_trace}
    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required(login_url='/session/login')
def trace_list(request, board_url, item_per_page=20):
    if not _check_valid(request, board_url):
        return HttpResponse('Invalid access')
    board_post = BoardPost.objects.filter(
        board_post_trace__userprofile=request.user.userprofile,
        board_post_trace__is_trace=True)
    page = int(request.GET.get('page', 1))
    post_paginator = Paginator(board_post, item_per_page)
    post_list = []
    for post in post_paginator.page(page):
        post_list += [[post, post.get_is_read(request)]]
    return render(request,
                  'board/board_list.html',
                  {'post_list': post_list,
                   'current_page': page,
                   'pages': post_paginator.page_range})
