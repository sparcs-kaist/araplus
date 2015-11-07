# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from apps.channel.models import *
from apps.channel.backend import (
    _get_querystring,
    _parse_channel,
    _parse_post,
    _parse_comment,
    _write_channel,
    _subscribe_channel,
    _render_content,
    _get_post_list,
    _get_comment_list,
    _mark_read,
    _write_post,
    _write_comment,
    _delete_channel,
    _delete_content,
    _mark_adult,
    _vote_post,
    _vote_comment,
    _get_post_log,
    _get_comment_log,
    _report,
)
import json
from apps.channel.forms import *


@login_required(login_url='/session/login')
def home(request):
    channel_list = Channel.objects.filter(is_deleted=False)
    return render(request, 'channel/main.html',
                  {'channel_list': channel_list})


@login_required(login_url='/session/login')
def create(request):
    if request.method == 'POST':
        result = _write_channel(request)
        if 'success' in result:
            return redirect('../' + result['success'].url + '/')

        form_channel = result['fail']
    else:
        form_channel = ChannelForm()

    return render(request, 'channel/channel.html',
                  {'channel_form': form_channel})


@login_required(login_url='/session/login')
def list(request, channel_url):
    channel_list = Channel.objects.filter()
    channel = _parse_channel(channel_url)

    notice_list, post_list, pages, page = _get_post_list(request, channel)
    querystring = _get_querystring(request, 'page')
    return render(request, 'channel/list_core.html',
                  {'notice_list': notice_list,
                   'post_list': post_list,
                   'channel_list': channel_list,
                   'current_channel': channel,
                   'pages': pages,
                   'current_page': page,
                   'is_admin': channel.admin == request.user.userprofile,
                   'querystring': querystring})


@login_required(login_url='/session/login')
def subscribe_channel(request, channel_url):
    channel = _parse_channel(channel_url)
    _subscribe_channel(request, channel, True)
    return redirect('http://naver.com')


@login_required(login_url='/session/login')
def unsubscribe_channel(request, channel_url):
    channel = _parse_channel(channel_url)
    _subscribe_channel(request, channel, False)
    return redirect('http://naver.com')

@login_required(login_url='/session/login')
def write_post(request, channel_url):
    channel = _parse_channel(channel_url)
    if channel.admin.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        result = _write_post(request, channel)
        if 'success' in result:
            channel_post_trace = ChannelPostTrace(
                    channel_post=result['success'],
                    userprofile=request.user.userprofile)
            channel_post_trace.save()
            return redirect('../' + str(result['success'].order) + '/')

        form_content, form_post, form_attachment = result['fail']
    else:
        form_content = ChannelContentForm()
        form_post = ChannelPostForm(initial={'channel': channel.id})
        form_attachment = ChannelAttachmentForm()

    return render(request, 'channel/write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment,
                   'channel': channel})


@require_POST
@login_required(login_url='/session/login')
def write_comment(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    _write_comment(request, channel_url, post)
    querystring = _get_querystring(request, 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def read_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order, live_only=False)
    channel_list = Channel.objects.all()
    post_rendered = _render_content(request.user.userprofile, post=post)
    _mark_read(request.user.userprofile, post)
    comments, c_pages, c_page = _get_comment_list(request, post)
    notice_list, post_list, pages, page = _get_post_list(request, channel)
    report_form = ChannelReportForm()

    next_post = int(post_order) + 1
    prev_post = int(post_order) - 1
    if next_post > len(post_list):
        next_post = 0

    try:
        channel_post_trace = ChannelPostTrace.objects.get(
                userprofile=request.user.userprofile,
                channel_post__id=post_id)
    except:
        channel_post_trace = None

    querystring = _get_querystring(request, 'page')
    return render(request, 'channel/read.html',
                  {
                      'querystring': querystring,
                      'post': post_rendered,
                      'channel_post_trace': channel_post_trace,
                      'comment_list': comments,
                      'notice_list': notice_list,
                      'post_list': post_list,
                      'pages': pages,
                      'current_page': page,
                      'c_pages': c_pages,
                      'current_c_page': c_page,
                      'channel_list': channel_list,
                      'current_channel': channel,
                      'report_form': report_form,
                      'next_post' : next_post,
                      'prev_post' : prev_post
                  })


@login_required(login_url='/session/login')
def modify_channel(request, channel_url):
    channel = _parse_channel(channel_url)
    if channel.admin != request.user.userprofile:
        raise PermissionDenied

    if request.method == 'POST':
        result = _write_channel(request, channel)
        if 'success' in result:
            return redirect('../../' + result['success'].url + '/')

        form_channel = result['fail']
    else:
        form_channel = ChannelForm(instance=channel)

    return render(request, 'channel/channel.html',
                  {'channel_form': form_channel})


@login_required(login_url='/session/login')
def modify_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    if post.author != request.user.userprofile:
        raise PermissionDenied

    if request.method == 'POST':
        result = _write_post(request, channel, post)

        if 'success' in result:
            return redirect('../')

        form_content, form_post, form_attachment = result['fail']
    else:
        form_content = ChannelContentForm(instance=post.channel_content)
        form_post = ChannelPostForm(instance=post)
        form_attachment = ChannelAttachmentForm()

    return render(request, 'channel/write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment,
                   'channel': channel.id})


@require_POST
@login_required(login_url='/session/login')
def modify_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if comment.author != request.user.userprofile:
        raise PermissionDenied

    _write_comment(request, comment=comment)
    querystring = _get_querystring(request, 'page')
    return redirect('../../' + querystring)


@require_POST
@login_required(login_url='/session/login')
def delete_channel(request, channel_url):
    channel = _parse_channel(channel_url)
    if channel.admin != request.user.userprofile:
        raise PermissionDenied

    _delete_channel(channel)
    return HttpResponse(status=200)


@require_POST
@login_required(login_url='/session/login')
def delete_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    if post.author != request.user.userprofile:
        raise PermissionDenied

    _delete_content(post.channel_content)
    return HttpResponse(status=200)


@require_POST
@login_required(login_url='/session/login')
def delete_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if comment.author != request.user.userprofile:
        raise PermissionDenied

    _delete_content(comment.channel_content)
    return HttpResponse(status=200)


@login_required(login_url='/session/login')
def log_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    post, modify_log = _get_post_log(post)
    return render(request, "channel/log_post.html",
                  {'post': post, 'modify_log': modify_log})


@login_required(login_url='/session/login')
def log_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    comment, modify_log = _get_comment_log(comment)
    return render(request, "channel/log_comment.html",
                  {'comment': comment, 'modify_log': modify_log})


@require_POST
@login_required(login_url='/session/login')
def mark19_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    result = _mark_adult(request.user.userprofile, post.channel_content)
    if result:
        return HttpResponse(status=200)
    return HttpResponse(status=400)

@require_POST
@login_required(login_url='/session/login')
def mark19_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    result = _mark_adult(request.user.userprofile, comment.channel_content)
    if result:
        return HttpResponse(status=200)
    return HttpResponse(status=400)


@require_POST
@login_required(login_url='/session/login')
def vote_post(request, channel_url, post_order):
    print 1
    channel, post = _parse_post(channel_url, post_order)
    result = _vote_post(request.user.userprofile, post)
    return JsonResponse(result)


@require_POST
@login_required(login_url='/session/login')
def vote_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    is_up = request.POST.get('up', '0')
    if is_up not in ['0', '1']:
        raise PermissionDenied

    result = _vote_comment(request.user.userprofile, comment, is_up)
    return JsonResponse(result)


@require_POST
@login_required(login_url='/session/login')
def report_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    _report(request, post.channel_content)
    return HttpResponse(status=200)


@require_POST
@login_required(login_url='/session/login')
def report_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    _report(request, comment.channel_content)
    return HttpResponse(status=200)

@login_required(login_url='/session/login')
def trace(request, channel_url, post_id):
    if not _check_valid(request, channel_url):
        return HttpResponse('Invalid access')
    request_type = request.POST.get('type', '')
    try:
        channel_post_trace = ChannelPostTrace.objects.get(
                userprofile=request.user.userprofile,
                channel_post__id=post_id)
        if request_type == 'trace':
            channel_post_trace.is_trace = not(channel_post_trace.is_trace)
        elif request_type == 'alarm':
            channel_post_trace.is_notified = not(channel_post_trace.is_notified)
        else:
            result = {'message': 'failed'}
            return HttpResponse(json.dumps(result),
                    content_type='application/json')
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
def trace_list(request, channel_url, item_per_page=20):
    if not _check_valid(request, channel_url):
        return HttpResponse('Invalid access')
    channel_post = ChannelPost.objects.filter(
            channel_post_trace__userprofile=request.user.userprofile,
            channel_post_trace__is_trace=True)
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
