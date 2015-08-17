# -*- coding: utf-8
from apps.channel.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import diff_match_patch
from django.db.models import Q
from apps.channel.forms import *
from itertools import izip


def _get_post_list(request, channel_url='', item_per_page=15):
    adult_filter = request.GET.get('adult_filter')
    best_filter = bool(request.GET.get('best', False))
    page = int(request.GET.get('page', 1))
    search_tag = request.GET.get('tag', '')
    search_title = request.GET.get('title', '')
    search_content = request.GET.get('content', '')  # title + content
    search_nickname = request.GET.get('nickname', '')
    try:
        channel = Channel.objects.get(url=channel_url)
    except:
        return ([], [], None, None)  # Wrong channel request
    if channel.is_deleted:
        return ([], [], None, None)
    channel_post_notice = ChannelPost.objects.filter(is_notice=True,
                                                     channel=channel)
    channel_post = ChannelPost.objects.filter(channel=channel)
    # search
    if best_filter:
        channel_post = channel_post.filter(is_best=True)
    if search_tag:
        channel_post = channel_post.filter(hashtag__tag_name=search_tag)
    if search_title:
        channel_post = channel_post.filter(title__contains=search_title)
    if search_content:
        channel_post = channel_post.filter(
            Q(channel_content__content__contains=search_content)
            | Q(title__contains=search_content))
    if search_nickname:
        channel_post = channel_post.filter(author__nickname=search_nickname,
                                           channel_content__is_anonymous=None)
    channel_post_notice = channel_post_notice[:5]
    post_paginator = Paginator(channel_post, item_per_page)
    post_list = []
    notice_list = []
    post_paged = post_paginator.page(page)
    current_page = post_paged.number
    for post in post_paged:
        post_list += [[post, post.get_is_read(request)]]
    for notice in channel_post_notice:
        notice_list += [[notice, notice.get_is_read(request)]]
    return notice_list, post_list, post_paginator.page_range, current_page


def _get_querystring(request, *args):
    query_list = []
    querystring = ''
    for field in args:
        if request.GET.get(field):
            query_list.append(field + '=' + request.GET[field])
    if query_list:
        querystring = '?' + '&'.join(query_list)
    return querystring

def _get_content(request, post_id):
    try:
        channel_post = ChannelPost.objects.get(id=post_id)
    except ObjectDoesNotExist:
        return ({}, [])
    if channel_post.channel.is_deleted:
        return ({}, [])
    try:
        channel_post_is_read = ChannelPostIs_read.objects.get(
            channel_post=channel_post,
            userprofile=request.user.userprofile)
    except ObjectDoesNotExist:
        channel_post_is_read = ChannelPostIs_read()
        channel_post_is_read.channel_post = channel_post
        channel_post_is_read.userprofile = request.user.userprofile
    channel_post_is_read.save()
    post = _get_post(request, channel_post, 'Post')
    comment_list = []
    order = 1
    for channel_comment in channel_post.channel_comment.all():
        comment = _get_post(request, channel_comment, 'Comment')
        comment['order'] = order
        order = order + 1
        comment_list.append(comment)
    best_comment = {}
    best_vote = 0
    for comment in comment_list:
        if comment['vote']['up'] > 5 and comment['vote']['up'] > best_vote:
            best_vote = comment['vote']['up']
            best_comment = comment
    if best_comment:
        best_comment['best_comment'] = True
        comment_list.insert(0, best_comment)
    return (post, comment_list)


def _get_post(request, channel_post, type):
    post = {}
    if type == 'Comment':
        pass
    elif type == 'Post':
        post['title'] = channel_post.title
        post['channel'] = channel_post.channel.kor_name
        post['channel_id'] = channel_post.channel.id
    else:
        return post
    userprofile = channel_post.author
    channel_content = channel_post.channel_content
    if channel_content.is_deleted:
        post['title'] = '--Deleted--'
        post['content'] = '--Deleted--'
    else:
        post['content'] = channel_content.replace_content_tags()
    post['id'] = channel_post.id
    post['deleted'] = channel_content.is_deleted
    post['content_id'] = channel_content.id
    post['created_time'] = channel_content.created_time
    post['username'] = userprofile.nickname
    if channel_content.is_anonymous:
        post['username'] = channel_content.is_anonymous
    post['return'] = (userprofile == request.user.userprofile)
    post['vote'] = channel_content.get_vote()
    post['vote']['is_up'] = False
    post['vote']['is_down'] = False
    try:
        is_vote = ChannelContentVote.objects.get(
                userprofile=userprofile, channel_content=channel_content)
        if is_vote.is_up:
            post['vote']['is_up'] = True
        else:
            post['vote']['is_down'] = True
    except ObjectDoesNotExist:
        pass
    post['adult'] = channel_content.is_adult
    return post


def _write_post(request, is_modify=False, post=None,
                content=None, channel=""):
    form_content = ChannelContentForm(
        request.POST,
        instance=content,
        is_modify=is_modify)
    form_post = ChannelPostForm(
        request.POST,
        instance=post)  # get form from post and instance
    form_attachment = ChannelAttachmentForm(request.POST, request.FILES)
    try:  # for modify log, get title and content before modify.
        # modify log for content
        content_before = content.content
        # modify log for post
        title_before = post.title
        channel_before = channel
    except:  # no such a content : is not modify
        if form_post.is_valid() and form_content.is_valid():
            if is_modify:
                content_diff = [[str(content.modified_time),
                                 _get_diff_match(content_before, content.content)]]
                channel_diff = [[0, channel_before]]
                post_diff = [[_get_diff_match(title_before, post.title),
                              channel_diff]]
                post.set_log(post_diff + post.get_log())
                content.set_log(content_diff + content.get_log())
            channel_post = form_post.save(
                author=request.user.userprofile,
                content=form_content.save(author=request.user.userprofile,
                                          post=post))  # save
            channel_content = channel_post.channel_content
            HashTag.objects.filter(channel_post=channel_post).delete()
            hashs = channel_content.get_hashtags()
            for tag in hashs:
                HashTag(tag_name=tag, channel_post=channel_post).save()
            form_attachment = ChannelAttachmentForm(request.POST, request.FILES)
            if form_attachment.is_valid():
                form_attachment.save(file=request.FILES['file'],
                                     content=channel_content)
            return {'save': channel_post}
        else:
            return {'failed': [form_content, form_post, form_attachment]}


def _write_comment(request, post_id, is_modify=False):
    user_profile = request.user.userprofile
    if is_modify:
        comment_id = request.POST.get('channel_comment_id', 0)
        try:
            channel_comment = ChannelComment.objects.get(id=comment_id)
            content_before = channel_comment.channel_content.content
            if channel_comment.author != user_profile:
                return  # wrong request
            content_form = ChannelContentForm(
                request.POST,
                instance=channel_comment.channel_content,
                is_modify=True)
        except ObjectDoesNotExist:
            return  # no comment
    else:
        try:
            channel_comment = ChannelComment(
                author=user_profile,
                channel_post=ChannelPost.objects.get(id=post_id))
            content_form = ChannelContentForm(request.POST)
        except:
            return  # no post
    if content_form.is_valid():
        if is_modify:
            channel_comment.channel_content.set_log(
                [[str(channel_comment.channel_content.modified_time),
                  _get_diff_match(content_before,
                                  channel_comment.channel_content.content)]] +
                  channel_comment.channel_content.get_log())
        channel_comment.channel_content = content_form.save(
            author=user_profile,
            post=channel_comment.channel_post)
    else:
        return  # Invalid form
        channel_comment.channel_content = content_form.save(
            author=user_profile,
            post=channel_comment.channel_post)
    channel_comment.channel_post.channel_content.save()  # update modified_time
    channel_comment.save()
    return channel_comment.channel_post.id


def _delete_post(request):
    # message = ''
    channel_content_id = request.POST.get('id', 0)
    try:
        channel_content = ChannelContent.objects.get(id=channel_content_id)
    except ObjectDoesNotExist:
        return 'no post or comment'
    if hasattr(channel_content, 'channel_post'):
        author = channel_content.channel_post.author
    elif hasattr(channel_content, 'channel_comment'):
        author = channel_content.channel_comment.author
    else:
        return 'invalid content'
    if author != request.user.userprofile:
        return 'not allowed'
    channel_content.is_deleted = True
    channel_content.save()
    return 'success'


def _report(request):
    content_id = request.POST.get('id', 0)
    report_form = ChannelReportForm(request.POST)
    print report_form.errors
    if report_form.is_valid():
        try:
            channel_content = ChannelContent.objects.get(id=content_id)
        except:
            return {'message': 'No content'}
        report_form.save(user=request.user.userprofile,
                         content=channel_content)
        return {'message': 'Success'}
    else:
        return {'message': 'Invalid form'}


def _vote(request):
    cancel = ''
    user_profile = request.user.userprofile
    vote_type = request.POST.get('vote_type', '')
    content_id = request.POST.get('vote_id', '')
    try:
        channel_content = ChannelContent.objects.get(id=content_id)
        if vote_type == 'up' or vote_type == 'down':
            is_up_or_down = (False, True)[vote_type == 'up']
            try:
                content_vote = ChannelContentVote.objects.get(
                    channel_content=channel_content,
                    userprofile=user_profile)
                if content_vote.is_up == is_up_or_down:
                    content_vote.delete()
                    return {'success': vote_type + ' canceled',
                            'vote': channel_content.get_vote(), 'cancel': 'yes'}
                else:
                    content_vote.is_up = is_up_or_down
                    content_vote.save()
                    _make_best(channel_content)
                    return {'success': 'changed to ' + vote_type,
                            'vote': channel_content.get_vote(), 'cancel': 'no'}
            except:
                cancel = 'no'
                vote = ChannelContentVote()
                vote.is_up = is_up_or_down
        elif vote_type == 'adult':
            if ChannelContentVoteAdult.objects.filter(
                    channel_content=channel_content,
                    userprofile=user_profile):
                return {'success': 'Already voted' + vote_type,
                        'vote': channel_content.get_vote()}
            else:
                vote = ChannelContentVoteAdult()
        elif vote_type == 'political':
            if ChannelContentVotePolitical.objects.filter(
                    channel_content=channel_content,
                    userprofile=user_profile):
                return {'success': 'Already voted ' + vote_type,
                        'vote': channel_content.get_vote()}
            else:
                vote = ChannelContentVotePolitical()
        else:
            return {'fail': 'Wrong request'}
        vote.channel_content = channel_content
        vote.userprofile = user_profile
        vote.save()
        _make_best(channel_content)
        return {'success': 'vote ' + vote_type,
                'vote': channel_content.get_vote(), 'cancel': cancel}
    except ObjectDoesNotExist:
        return {'fail': 'Unvalid ontent id'}


def _get_diff_match(before, after):  # get different match
    diff_obj = diff_match_patch.diff_match_patch()
    diff = diff_obj.diff_main(before, after)
    diff_obj.diff_cleanupSemantic(diff)
    new_diff = []
    for diff_element in diff:
        diff_element = list(diff_element)
        diff_element[1] = diff_element[1].replace("\r\n", " ")
        if diff_element[0] == 0 and len(diff_element[1]) >= 15:
            diff_element[1] = diff_element[1][0:5] + \
                '...' +\
                diff_element[1][-5:]
        new_diff = new_diff + [diff_element]
    return new_diff


def _get_post_log(post_id):
    diff_obj = diff_match_patch.diff_match_patch()
    channel_post = ChannelPost.objects.filter(id=post_id)[0]
    channel_content = channel_post.channel_content
    post = [channel_post.title,
            channel_post.channel.kor_name,
            channel_content.modified_time,
            channel_content.content]
    modify_log = []
    for log_post, log_content in izip(channel_post.get_log(),
                                      channel_content.get_log()):
        modify_log = modify_log +\
            [[diff_obj.diff_prettyHtml(log_post[0]),
              diff_obj.diff_prettyHtml(log_post[1]),
              diff_obj.diff_prettyHtml(log_post[2]),
              log_content[0],
              diff_obj.diff_prettyHtml(log_content[1])]]
    return post, modify_log


def _get_comment_log(comment_id):
    diff_obj = diff_match_patch.diff_match_patch()
    channel_comment = ChannelComment.objects.filter(id=comment_id)[0]
    channel_content = channel_comment.channel_content
    comment = [channel_content.modified_time,
               channel_content.content]
    modify_log = []
    for log_content in channel_content.get_log():
        modify_log = modify_log +\
            [[log_content[0], diff_obj.diff_prettyHtml(log_content[1])]]
    return comment, modify_log
