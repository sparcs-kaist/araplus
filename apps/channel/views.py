# -*- coding: utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.channel.models import *
from apps.channel.backend import (
    _get_post_list,
    _get_querystring,
    _get_content,
    _write_post,
    _delete_post,
    _report,
    _vote,
    _write_comment,
    _create_channel,
    _get_post_log,
    _get_comment_log,
    _remove_channel,
)
from itertools import izip
import json
import diff_match_patch
from apps.channel.forms import *
from django.core.paginator import Paginator


def home(request):
    # Should be show the list of channels
    return redirect('main/')


@login_required(login_url='/session/login')
def create_channel(request):
    if request.method == 'POST':
        result = _create_channel(request)
        if 'save' in result:
            return redirect('../' + result['save'].url + '/')
        else:
            form_channel = result['failed']
    else:
        form_channel = ChannelForm()
        return render(request,
                      'channel/create_channel.html',
                      {'channel_form': form_channel})


@login_required(login_url='/session/login')
def remove_channel(request, channel_url):
    return HttpResponse(_remove_channel(request, channel_url))


@login_required(login_url='/session/login')
def post_write(request, channel):
    if request.method == 'POST':
        result = _write_post(request, channel=channel)
        if 'save' in result:
            channel_post_trace = ChannelPostTrace(
                channel_post=result['save'],
                userprofile=request.user.userprofile)
            channel_post_trace.save()
            return redirect('../' + str(result['save'].id) + '/')
        else:
            form_content, form_post, form_attachment = result['failed']
    else:
        try:
            channel = Channel.objects.get(url=channel)
        except:
            channel = Channel.objects.get(id=1)
        form_content = ChannelContentForm()
        form_post = ChannelPostForm(initial={'channel': channel.id})
        form_attachment = ChannelAttachmentForm()
    return render(request,
            'channel/channel_write.html',
            {'content_form': form_content,
                'post_form': form_post,
                'attachment_form': form_attachment})


@login_required(login_url='/session/login')
def post_modify(request, post_id=0):
    post_instance = get_object_or_404(ChannelPost, id=post_id)
    if post_instance.author != request.user.userprofile:
        return redirect('../')
    if request.method == "POST":
        result = _write_post(request, True, post_instance,
                             post_instance.channel_content)
        if 'save' in result:  # success modify
            return redirect('../')
        else:
            form_content, form_post, form_attachment = result['failed']
    else:
        form_content = ChannelContentForm(
            is_modify=True,
            instance=post_instance.channel_content)
        form_post = ChannelPostForm(is_modify=True, instance=post_instance)
        form_attachment = ChannelAttachmentForm()
    return render(request,
                  'channel/channel_write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment})


@login_required(login_url='/session/login')
def post_read(request, channel_url, post_id):
    post, comment_list = _get_content(request, post_id)
    notice_list, post_list, pages, page = _get_post_list(request, channel_url)
    channel_list = Channel.objects.all()
    try:
        channel_post_trace = ChannelPostTrace.objects.get(
            userprofile=request.user.userprofile,
            channel_post__id=post_id)
    except:
        channel_post_trace = None
    try:
        current_channel = channel_list.get(url=channel_url)
        print current_channel
    except:
        current_channel = None
    querystring = _get_querystring(request, 'best', 'page')
    # tested for report ########
    report_form = ChannelReportForm()
    """return render(request,
                  'channel/modal_test.html',
                  {'report_form': report_form})"""
    #################################
    return render(request,
                  'channel/channel_read.html',
                  {
                      'querystring': querystring,
                      'post': post,  # post for post
                      'comment_list': comment_list,  # comment for post
                      'channel_post_trace': channel_post_trace,
                      # Below,there are thing for postList.
                      'notice_list': notice_list,
                      'post_list': post_list,
                      'pages': pages,
                      'current_page': page,
                      'channel_list': channel_list,
                      'current_channel': current_channel,
                      'report_form': report_form
                  })


@login_required(login_url='/session/login')
def post_modify_log(request, channel_url, post_id):
    post, modify_log = _get_post_log(post_id)
    return render(request, "channel/post_log.html",
                  {
                      'post': post,
                      'modify_log': modify_log,
                  })


@login_required(login_url='/session/login')
def comment_modify_log(request, channel_url, comment_id):
    comment, modify_log = _get_comment_log(comment_id)
    return render(request, "channel/comment_log.html",
                  {
                      'comment': comment,
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
def post_list(request, channel_url):
    notice_list, post_list, pages, page = _get_post_list(request, channel_url)
    channel_list = Channel.objects.filter(is_official=True)
    try:
        current_channel = Channel.objects.get(url=channel_url, is_deleted=False)
    except:
        current_channel = None
    querystring = _get_querystring(request, 'best', 'page')
    return render(request,
            'channel/channel_list.html',
            {'notice_list':  notice_list,
                'post_list': post_list,
                'channel_list': channel_list,
                'current_channel': current_channel,
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
    request_type = request.POST.get('type', '')
    print request_type
    try:
        channel_post_trace = ChannelPostTrace.objects.get(
            userprofile=request.user.userprofile,
            channel_post__id=post_id)
        print channel_post_trace.id
        if request_type == 'trace':
            channel_post_trace.is_trace = not(channel_post_trace.is_trace)
        elif request_type == 'alarm':
            channel_post_trace.is_notified = not(channel_post_trace.is_notified)
        else:
            result = {'message': 'failed'}
            return HttpResponse(json.dumps(result), content_type='application/json')
        print channel_post_trace.id
    except:
        channel_post_trace = ChannelPostTrace(
                userprofile=request.user.userprofile,
                channel_post_id=post_id)
        if request_type == 'alarm':
            channel_post_trace.is_notified = True
    channel_post_trace.save()
    result = {
        'message': 'success',
        'alarm': channel_post_trace.is_notified,
        'trace': channel_post_trace.is_trace}
    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required(login_url='/session/login')
def trace_list(request, item_per_page=20):
    channel_post = ChannelPost.objects.filter(
        channel_post_trace__userprofile=request.user.userprofile,
        channel_post_trace__is_trace=True)
    print channel_post
    page = int(request.GET.get('page', 1))
    post_paginator = Paginator(channel_post, item_per_page)
    post_list = []
    for post in post_paginator.page(page):
        post_list += [[post, post.get_is_read(request)]]
    return render(request,
                  'channel/channel_list.html',
                  {'post_list': post_list,
                   'current_page': page,
                   'pages': post_paginator.page_range})
