# -*- coding: utf-8
from apps.channel.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
import diff_match_patch
from django.db.models import Q
from apps.channel.forms import *
from itertools import izip


def _get_channel(channel_url):
    try:
        return Channel.objects.get(url=channel_url, is_deleted=False)
    except:
        return None


def _get_post(post_id):
    try:
        return ChannelPost.objects.get(id=post_id)
    except:
        return None
    

def _get_comment(comment_id):
    try:
        return ChannelComment.objects.get(id=comment_id)
    except:
        return None


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
    
    if content.is_deleted:
        data['title'] = '--Deleted--'
        data['content'] = '--Deleted--'
    else:
        data['content'] = content.replace_content_tags()
    
    data['id'] = raw_data.id
    data['deleted'] = content.is_deleted
    data['content_id'] = content.id
    data['created_time'] = content.created_time
    data['username'] = author.nickname
    data['is_adult'] = content.is_adult
    data['auth'] = (userprofile == author)
    print data
    return data


def _get_querystring(request, *args):
    query_list = []
    querystring = ''
    for field in args:
        if request.GET.get(field):
            query_list.append(field + '=' + request.GET[field])
    
    if query_list:
        querystring = '?' + '&'.join(query_list)
    return querystring


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
        post_list += [[post, post.get_is_read(request)]]

    return notice_list, post_list, paginator.page_range, current_page


def _write_post(request, channel, is_modify=False, content=None, post=None):
    form_content = ChannelContentForm(request.POST, instance=content)
    form_post = ChannelPostForm(request.POST, instance=post)
    form_attachment = ChannelAttachmentForm(request.POST, request.FILES)

    try:
        content_before = content.content
        title_before = post.title
    except:
        pass

    if form_post.is_valid() and form_content.is_valid():
        if is_modify:
            post_diff = [[_get_diff_match(title_before, post.title)]]
            content_diff = [[str(content.modified_time),
                _get_diff_match(content_before, content.content)]]

            post.set_log(post_diff + post.get_log())
            content.set_log(content_diff + content.get_log())
        
        channel_content = form_content.save()

        channel_post = form_post.save(channel=channel, 
                author=request.user.userprofile, 
                content = channel_content)
        
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


def _get_comments(request, post):
    comment_list = []
    order = 1
    for comment in post.channel_comment.all():
        comment = _render_content(request.user.userprofile, comment=comment)
        comment['order'] = order
        order = order + 1
        comment_list.append(comment)

    """best_comment = {}
    best_vote = 0
    for comment in comment_list:
        if comment['vote']['up'] > 5 and comment['vote']['up'] > best_vote:
            best_vote = comment['vote']['up']
            best_comment = comment

    if best_comment:
        best_comment['best_comment'] = True
        comment_list.insert(0, best_comment)"""
    return comment_list


def _mark_read(userprofile, post):
    try:
        is_read = ChannelPostIsRead.objects.get(
                channel_post=post, userprofile=userprofile)
    except ObjectDoesNotExist:
        is_read = ChannelPostIsRead()
        is_read.channel_post = post
        is_read.userprofile = userprofile
    is_read.save()


def _write_comment(request, post=None, comment=None):
    userprofile = request.user.userprofile
    
    if comment != None:
        content_before = comment.channel_content.content
        if comment.author != userprofile:
            return

        content_form = ChannelContentForm(request.POST,
                instance=comment.channel_content)
    else:
        content_form = ChannelContentForm(request.POST)
    
    if not content_form.is_valid():
        return

    if comment != None:
        comment.channel_content.set_log(
            [[str(comment.channel_content.modified_time),
              _get_diff_match(content_before,
                              comment.channel_content.content)]] +
             comment.channel_content.get_log())
    else:
        comment = ChannelComment(channel_post=post, author=userprofile)
    
    comment.channel_content = content_form.save()
    comment.save()
    
   
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
        if vote_type == 'rating':
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
