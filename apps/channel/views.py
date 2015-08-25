# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from apps.channel.models import *
from apps.channel.backend import (
    _get_querystring,
    _parse_channel,
    _parse_post,
    _parse_comment, 
    _get_post_list,
    _write_post,
)
import json
from apps.channel.forms import *


@login_required(login_url='/session/login')
def home(request):
    channel_list = Channel.objects.all()
    return render(request, 'channel/main.html',
                  {'channel_list': channel_list})


@login_required(login_url='/session/login')
def list(request, channel_url):
    channel_list = Channel.objects.filter()
    channel = _parse_channel(channel_url)
    if not channel:
        raise Http404

    notice_list, post_list, pages, page = _get_post_list(request, channel)
    querystring = _get_querystring(request, 'page')
    return render(request, 'channel/list.html',
                  {'notice_list': notice_list,
                   'post_list': post_list,
                   'channel_list': channel_list,
                   'current_channel': channel,
                   'pages': pages,
                   'current_page': page,
                   'querystring': querystring})


@login_required(login_url='/session/login')
def write_post(request, channel_url):
    channel = _parse_channel(channel_url)
    if not channel:
        raise Http404

    if channel.admin.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        result = _write_post(request, channel)
        if 'success' in result:
            return redirect('../' + str(result['success'].channel_content.id) + '/')

        form_content, form_post, form_attachment = result['failed']
    else:
        form_content = ChannelContentForm()
        form_post = ChannelPostForm(initial={'channel': channel.id})
        form_attachment = ChannelAttachmentForm()

    return render(request, 'channel/write.html',
                  {'content_form': form_content,
                   'post_form': form_post,
                   'attachment_form': form_attachment,
                   'channel': channel.id})


@login_required(login_url='/session/login')
def write_comment(request, channel_url, post_order):
    if request.method != 'POST':
        return redirect('../')

    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404

    _write_comment(request, post)
    querystring = _get_querystring(request, 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def read_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order, live_only=False)
    if not post:
        raise Http404

    post_rendered = _render_content(request.user.userprofile, post=post)
    _mark_read(request.user.userprofile, post)
    comments = _get_comments(request, post)
    notice_list, post_list, pages, page = _get_post_list(request, channel)
    report_form = ChannelReportForm()

    querystring = _get_querystring(request, 'page')
    return render(request, 'channel/read.html',
                  {
                      'querystring': querystring,
                      'post': post_rendered,
                      'comment_list': comments,
                      'notice_list': notice_list,
                      'post_list': post_list,
                      'pages': pages,
                      'current_page': page,
                      'channel_list': channel_list,
                      'current_channel': channel,
                      'report_form': report_form
                  })


@login_required(login_url='/session/login')
def modify_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404

    if post.author != request.user.userprofile:
        raise PermissionDenied

    if request.method == 'POST':
        result = _write_post(request, channel, post)

        if 'success' in result:
            return redirect('../')
        else:
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


@login_required(login_url='/session/login')
def modify_comment(request, channel_url, post_order, comment_order):
    if request.method != 'POST':
        raise PermissionDenied

    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if not comment:
        raise Http404

    if comment.author != request.user.userprofile:
        raise PermissionDenied

    _write_comment(request, comment=comment)
    querystring = _get_querystring(request, 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def delete_post(request, channel_url, post_order):
    if request.method != 'POST':
        raise PermissionDenied()

    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404
    
    if post.author != request.user.userprofile:
        raise PermissionDenied

    _delete_content(post.channel_content)


@login_required(login_url='/session/login')
def delete_comment(request, channel_url, post_order, comment_order):
    if request.method != 'POST':
        raise PermissionDenied()

    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if not comment:
        raise Http404
    
    if comment.author != request.user.userprofile:
        raise PermissionDenied

    _delete_content(comment.channel_content)


@login_required(login_url='/session/login')
def log_post(request, channel_url, post_order):
    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404

    post, modify_log = _get_post_log(post)
    return render(request, "channel/post_log.html",
                  {'post': post, 'modify_log': modify_log})


@login_required(login_url='/session/login')
def log_comment(request, channel_url, post_order, comment_order):
    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if not comment:
        raise Http404

    comment, modify_log = _get_comment_log(comment)
    return render(request, "channel/comment_log.html",
                  {'comment': comment, 'modify_log': modify_log})


@login_required(login_url='/session/login')
def mark19_post(request, channel_url, post_order):
    if request.method != 'POST':
        raise PermissionDenied

    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404

    _mark_adult(request.user.userprofile, post.channel_content)


@login_required(login_url='/session/login')
def mark19_comment(request, channel_url, post_order, comment_order):
    if request.method != 'POST':
        raise PermissionDenied

    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if not comment:
        raise Http404

    _mark_adult(request.user.userprofile, comment.channel_content)


@login_required(login_url='/session/login')
def vote_post(request, channel_url, post_order):
    if request.method != 'POST':
        raise PermissionDenied

    channel, post = _parse_post(channel_url, post_order)
    if not post:
        raise Http404

    rating = request.POST.get('rating', '1')
    if rating not in ['1', '2', '3', '4', '5']:
        raise PermissionDenied

    result = _vote_post(request.user.userprofile, post, rating)
    

@login_required(login_url='/session/login')
def vote_comment(request, channel_url, post_order, comment_order):
    if request.method != 'POST':
        raise PermissionDenied

    channel, post, comment = _parse_comment(channel_url, post_order, comment_order)
    if not comment:
        raise Http404

    is_up = request.POST.get('up', '0')
    if is_up not in ['0', '1']:
        raise PermissionDenied

    result = _vote_comment(request.user.userprofile, comment, is_up)


@login_required(login_url='/session/login')
def report(request, channel_url, content_id):
    if request.method == 'POST':
        message = _report(request)
    return HttpResponse(json.dumps(message), content_type='application/json')
