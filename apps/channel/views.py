# -*- coding: utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseForbidden
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
    _get_post_log,
    _get_comment_log,
)
from itertools import izip
import json
import diff_match_patch
from apps.channel.forms import *
from django.core.paginator import Paginator


@login_required(login_url='/session/login')
def home(request):
    channel_list = Channel.objects.all()
    return render(request, 'channel/main.html',
            {'channel_list': channel_list})


@login_required(login_url='/session/login')
def post_write(request, channel_url):
    try:
        channel = Channel.objects.get(url=channel_url)
    except:
        raise Http404
  
    if channel.admin.user != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        if str(channel.id) != request.POST.get('channel', '-1'):
            return HttpResponseForbidden()

        result = _write_post(request, channel=channel_url)
        if 'save' in result:
            channel_post_trace = ChannelPostTrace(
                channel_post=result['save'],
                userprofile=request.user.userprofile)
            channel_post_trace.save()
            return redirect('../' + str(result['save'].id) + '/')
        
        form_content, form_post, form_attachment = result['failed']
    else:
        form_content = ChannelContentForm()
        form_post = ChannelPostForm(initial={'channel': channel.id})
        form_attachment = ChannelAttachmentForm()
    
    return render(request,
            'channel/channel_write.html',
            {'content_form': form_content,
                'post_form': form_post,
                'attachment_form': form_attachment,
                'channel': channel.id})


@login_required(login_url='/session/login')
def post_modify(request, post_id=0):
    post_instance = get_object_or_404(ChannelPost, id=post_id)
    if post_instance.author != request.user.userprofile:
        return redirect('../')
    if request.method == "POST":
        if str(post_instance.channel.id) != request.POST.get('channel', '-1'):
            return HttpResponseForbidden()

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
                   'attachment_form': form_attachment,
                   'channel': post_instance.channel.id})


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
    querystring = _get_querystring(request, 'page')
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
    querystring = _get_querystring(request, 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def comment_modify(request, post_id):
    if request.method == 'POST':
        post_id = _write_comment(request, post_id, True)
    querystring = _get_querystring(request, 'page')
    return redirect('../' + querystring)


@login_required(login_url='/session/login')
def post_list(request, channel_url):
    notice_list, post_list, pages, page = _get_post_list(request, channel_url)
    channel_list = Channel.objects.filter()
    try:
        current_channel = Channel.objects.get(url=channel_url, is_deleted=False)
    except:
        raise Http404
    querystring = _get_querystring(request, 'page')
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
