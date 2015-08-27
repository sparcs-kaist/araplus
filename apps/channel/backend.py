# -*- coding: utf-8
from apps.channel.models import *
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
import diff_match_patch
from django.db.models import Q
from apps.channel.forms import *
from itertools import izip


def _get_querystring(request, *args):
    query_list = []
    querystring = ''
    for field in args:
        if request.GET.get(field):
            query_list.append(field + '=' + request.GET[field])

    if query_list:
        querystring = '?' + '&'.join(query_list)
    return querystring


def _parse_channel(channel_url):
    try:
        return Channel.objects.get(url=channel_url, is_deleted=False)
    except:
        raise Http404


def _parse_post(channel_url, post_order, live_only=True):
    channel = _parse_channel(channel_url)
    
    try:
        post = ChannelPost.objects.get(channel=channel, order=post_order)
        if live_only and post.channel_content.is_deleted:
            raise Http404

        return channel, post
    except:
        raise Http404


def _parse_comment(channel_url, post_order, comment_order, live_only=True):
    channel, post = _parse_post(channel_url, post_order, live_only)

    try:
        comment = ChannelComment.objects.get(channel_post=post,
                order=int(comment_order))
        if live_only and comment.channel_content.is_deleted:
            raise Http404

        return channel, post, comment
    except:
        raise Http404


def _write_channel(request, channel=None):
    form_channel = ChannelForm(request.POST, instance=channel)

    if form_channel.is_valid():
        channel = form_channel.save(admin=request.user.userprofile)
        return {'success': channel}
    else:
        return {'fail': form_channel}


def _render_content(userprofile, post=None, comment=None):
    if not post and not comment:
        return None

    if post:
        raw_data = post
    else:
        raw_data = comment

    author = raw_data.author
    content = raw_data.channel_content

    data = {}
    if post:
        data['title'] = raw_data.title
        data['rating'] = raw_data.get_my_rating(userprofile)
        data['rating_avg'] = raw_data.get_rating()
    else:
        data['vote'] = raw_data.get_my_vote(userprofile)
        data['vote_up'], data['vote_down'] = raw_data.get_vote()

    if content.is_deleted:
        data['title'] = '--Deleted--'
        data['content'] = '--Deleted--'
    else:
        data['content'] = content.replace_content_tags()

    data['id'] = raw_data.id
    data['order'] = raw_data.order
    data['deleted'] = content.is_deleted
    data['content_id'] = content.id
    data['created_time'] = content.created_time
    data['username'] = author.nickname
    data['is_adult'] = content.is_adult
    data['mark19'] = content.is_mark19(userprofile)
    data['auth'] = (userprofile == author)
    return data


def _get_post_list(request, channel, item_per_page=15):
    adult_filter = request.GET.get('adult_filter')

    page = int(request.GET.get('page', 1))
    search_tag = request.GET.get('tag', '')
    search_title = request.GET.get('title', '')
    search_content = request.GET.get('content', '')  # title + content
    search_nickname = request.GET.get('nickname', '')

    post_notice = ChannelPost.objects.filter(channel=channel, is_notice=True)[:5]
    post = ChannelPost.objects.filter(channel=channel)

    if search_tag:
        post = post.filter(hashtag__tag_name=search_tag)
    if search_title:
        post = post.filter(title__contains=search_title)
    if search_content:
        post = post.filter(
                Q(channel_content__content__contains=search_content)
                | Q(title__contains=search_content))
    if search_nickname:
        post = post.filter(author__nickname=search_nickname,
                           channel_content__is_anonymous=None)

    paginator = Paginator(post, item_per_page)
    try:
        post_paged = paginator.page(page)
    except EmptyPage:
        post_paged = paginator.page(paginator.num_pages)
    current_page = post_paged.number

    post_list = []
    notice_list = []
    for notice in post_notice:
        notice_list += [[notice, notice.get_is_read(request)]]
    for post in post_paged:
        post.content_id = post.channel_content.id
        post_list += [[post, post.get_is_read(request)]]

    return notice_list, post_list, paginator.page_range, current_page


def _get_comment_list(request, post):
    comment_list = []
    for comment in post.channel_comment.all():
        comment = _render_content(request.user.userprofile, comment=comment)
        comment_list.append(comment)

    best_comments = reversed(sorted(
        filter(lambda x: x['vote_up'] > 5, comment_list),
        key=lambda x: x['vote_up'] - x['vote_down']))

    return list(best_comments) + comment_list


def _mark_read(userprofile, post):
    try:
        is_read = ChannelPostIsRead.objects.get(
                channel_post=post, userprofile=userprofile)
    except ObjectDoesNotExist:
        is_read = ChannelPostIsRead()
        is_read.channel_post = post
        is_read.userprofile = userprofile
    is_read.save()


def _write_post(request, channel, post=None):
    content = None
    if post:
        content = post.channel_content
        content_before = content.content
        title_before = post.title

    form_content = ChannelContentForm(request.POST, instance=content)
    form_post = ChannelPostForm(request.POST, instance=post)
    form_attachment = ChannelAttachmentForm(request.POST, request.FILES)

    if form_post.is_valid() and form_content.is_valid():
        if post:
            post_diff = [[_get_diff_match(title_before, post.title)]]
            content_diff = [[str(content.modified_time),
                _get_diff_match(content_before, content.content)]]

            post.set_log(post_diff + post.get_log())
            content.set_log(content_diff + content.get_log())

        content = form_content.save()
        post = form_post.save(channel=channel,
                author=request.user.userprofile,
                content=content)

        HashTag.objects.filter(channel_post=post).delete()
        hashs = content.get_hashtags()
        for tag in hashs:
            HashTag(tag_name=tag, channel_post=post).save()

        form_attachment = ChannelAttachmentForm(request.POST, request.FILES)
        if form_attachment.is_valid():
            form_attachment.save(file=request.FILES['file'],
                                 content=content)
        return {'success': post}
    else:
        return {'fail': [form_content, form_post, form_attachment]}


def _write_comment(request, post=None, comment=None):
    userprofile = request.user.userprofile

    if comment is not None:
        content_before = comment.channel_content.content
        if comment.author != userprofile:
            return False

        content_form = ChannelContentForm(request.POST,
                instance=comment.channel_content)
    else:
        content_form = ChannelContentForm(request.POST)

    if not content_form.is_valid():
        return False

    if comment is not None:
        comment.channel_content.set_log(
            [[str(comment.channel_content.modified_time),
              _get_diff_match(content_before,
                              comment.channel_content.content)]] +
             comment.channel_content.get_log())
    else:
        comment = ChannelComment(channel_post=post, author=userprofile)

    comment.channel_content = content_form.save()
    comment.save()
    return True


def _delete_channel(channel):
    channel.is_deleted = True
    channel.save()


def _delete_content(content):
    content.is_deleted = True
    content.save()


def _mark_adult(userprofile, content):
    try:
        marker = ChannelMarkAdult.objects.get(channel_content=content,
                userprofile=userprofile)
        return False
    except:
        marker = ChannelMarkAdult(channel_content=content,
                userprofile=userprofile)
        marker.save()
        return True


def _vote_post(userprofile, post, rating):
    try:
        vote = ChannelPostVote.objects.get(channel_post=post, userprofile=userprofile)
        if int(rating) == 0:
            vote.delete()
    except:
        vote = ChannelPostVote(channel_post=post, userprofile=userprofile)
    
    if int(rating) != 0:
        vote.rating = int(rating)
        vote.save()

    return {'rating': post.get_rating()}


def _vote_comment(userprofile, comment, is_up):
    up = (is_up == '0')
    result = {}

    try:
        vote = ChannelCommentVote.objects.get(channel_comment=comment,
                userprofile=userprofile)
        if vote.is_up == up:
            vote.delete()
            result['up'], result['down'] = False, False
    
    except:
        vote = ChannelCommentVote(channel_comment=comment,
                userprofile=userprofile)

    if 'up' not in result:
        vote.is_up = up
        vote.save()
        result['up'], result['down'] = vote.is_up, not vote.is_up

    result['tup'], result['tdown'] = comment.get_vote()
    return result


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


def _get_post_log(post):
    diff_obj = diff_match_patch.diff_match_patch()
    content = post.channel_content
    post_rendered = [post.title, content.modified_time, content.content]
    modify_log = []
    for log_post, log_content in izip(post.get_log(), content.get_log()):
        modify_log = modify_log +\
            [[diff_obj.diff_prettyHtml(log_post[0]),
              log_content[0],
              diff_obj.diff_prettyHtml(log_content[1])]]
    return post_rendered, modify_log


def _get_comment_log(comment):
    diff_obj = diff_match_patch.diff_match_patch()
    content = comment.channel_content
    comment = [content.modified_time, content.content]
    modify_log = []
    for log_content in content.get_log():
        modify_log = modify_log +\
            [[log_content[0], diff_obj.diff_prettyHtml(log_content[1])]]
    return comment, modify_log


def _report(request, content):
    report_form = ChannelReportForm(request.POST)
    if report_form.is_valid():
        report_form.save(user=request.user.userprofile, content=content)
        return True
    return False
