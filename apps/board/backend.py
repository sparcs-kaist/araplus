# -*- coding: utf-8
from apps.board.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import diff_match_patch
from django.db.models import Q
from apps.board.forms import *
from itertools import izip
from notifications import notify
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.encoding import uri_to_iri, iri_to_uri
from django.utils.http import urlquote
import django_summernote.models as summernote
import re
import os


imtag_regex = re.compile("<img.+?src=[\"'](.+?)[\"'].*?>")

POINTS_POST_WRITE = 5
POINTS_COMMENT_WRITE = 3
POINTS_POST_DELETE = -5
POINTS_VOTED_UP = 3
POINTS_VOTE_DOWN = -1
POINTS_VOTED_DOWN = -2


def _get_post_list(request, board_url='', item_per_page=15, trace=False):
    # Adult filter 현재 사용하지 않음.
    # adult_filter = request.GET.get('adult_filter')
    best_filter = bool(request.GET.get('best', False))
    page = int(request.GET.get('page', 1))
    search_tag = request.GET.get('tag', '')
    search_title = request.GET.get('title', '')
    search_content = request.GET.get('content', '')  # title + content
    search_nickname = request.GET.get('nickname', '')
    search_category = request.GET.get('category', '')
    if board_url != 'all':
        try:
            board = Board.objects.get(url=board_url)
        except:
            return ([], [], None, None)  # Wrong board request
    if trace:
        board_post_notice = []
        board_post = request.user.userprofile.board_post.all()
    else:
        if board_url == 'all':
            board_post_notice = BoardPost.objects.filter(
                is_notice=True,
                board__is_deleted=False,
                board__is_official=True)
            board_post = BoardPost.objects.filter(
                board__is_deleted=False,
                board__is_official=True)
        else:
            board_post_notice = BoardPost.objects.filter(is_notice=True,
                                                         board=board)
            board_post = BoardPost.objects.filter(board=board)
    # search
    if best_filter:
        board_post = board_post.filter(is_best=True)
        board_post_notice = board_post_notice.filter(is_best=True)
    
    if search_tag:
        board_post = board_post.filter(hashtag__tag_name=search_tag)
        board_post_notice = board_post_notice.filter(hashtag__tag_name=search_tag)

    if search_title:
        board_post = board_post.filter(title__contains=search_title)
        board_post_notice = board_post_notice.filter(title__contains=search_title)

    if search_content:
        board_post = board_post.filter(
            Q(board_content__content__contains=search_content)
            | Q(title__contains=search_content))
        board_post_notice = board_post_notice.filter(
            Q(board_content__content__contains=search_content)
            | Q(title__contains=search_content))

    if search_nickname:
        board_post = board_post.filter(author__nickname=search_nickname,
                                       board_content__is_anonymous=None)
        board_post_notice = board_post_notice.filter(author__nickname=search_nickname,
                                       board_content__is_anonymous=None)
    if search_category:
        board_post = board_post.filter(board_category__name=search_category)
        board_post_notice = board_post_notice.filter(board_category__name=search_category) 
    board_post_notice = board_post_notice[:5]
    post_paginator = Paginator(board_post, item_per_page)
    post_list = []
    notice_list = []
    post_paged = post_paginator.page(page)
    current_page = post_paged.number
    for post in post_paged:
        post_list += [[post, post.get_is_read(request)]]
    for notice in board_post_notice:
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


def _get_content(request, post_id, comment_per_page=10):
    try:
        board_post = BoardPost.objects.get(id=post_id)
    except ObjectDoesNotExist:
        return ({}, [])
    if board_post.board.is_deleted:
        return ({}, [])
    try:
        board_post_is_read = BoardPostIs_read.objects.get(
            board_post=board_post,
            userprofile=request.user.userprofile)
        last_read = board_post_is_read.last_read
    except ObjectDoesNotExist:
        board_post_is_read = BoardPostIs_read()
        board_post_is_read.board_post = board_post
        board_post_is_read.userprofile = request.user.userprofile
        last_read = timezone.now()
    recent_comment = True
    post = _get_post(request, board_post, 'Post')
    # pagination of comments
    board_comments = board_post.board_comment.all()
    comment_list = []
    comment_nickname_list = []
    if board_post.board_content.is_anonymous is None:
        comment_nickname_list = [(board_post.author.nickname, 0)]
    order = 1
    for board_comment in board_comments:
        comment = _get_post(request, board_comment, 'Comment',
                            comment_nickname_list)
        comment['order'] = order
        comment_list.append(comment)
        # 현재 글에 달린 댓글의 닉네임 리스트
        if comment['is_anonymous'] is None:
            username = comment['username']
            comment_nickname_list.append((username, order))
        order = order + 1
        if board_comment.board_content.created_time > last_read:
            comment['recent_comment'] = recent_comment
            recent_comment = False
        else:
            comment['recent_comment'] = False
    best_comment = {}
    best_vote = 0
    for comment in comment_list:
        if comment['vote']['up'] > 5 and comment['vote']['up'] > best_vote:
            best_vote = comment['vote']['up']
            best_comment = comment
    if best_comment:
        best_comment['best_comment'] = True
        comment_list.insert(0, best_comment)
    board_post_is_read.save()
    return (post, comment_list)


def _get_post(request, board_post, target_type, comment_nickname_list=[]):
    post = {}
    if target_type == 'Comment':
        pass
    elif target_type == 'Post':
        post['title'] = board_post.title
        post['board'] = board_post.board.kor_name
        post['board_id'] = board_post.board.id
        try:
            post['category'] = board_post.board_category.name
        except:
            post['category'] = ''
    else:
        return post
    userprofile = board_post.author
    board_content = board_post.board_content
    if board_content.is_deleted:
        post['title'] = '--Deleted--'
        post['content'] = '--Deleted--'
    else:
        post['content'] = board_content.replace_content_tags(
            target_type, comment_nickname_list)
    post['id'] = board_post.id
    post['deleted'] = board_content.is_deleted
    post['content_id'] = board_content.id
    post['created_time'] = board_content.created_time
    post['username'] = userprofile.nickname
    if board_content.is_anonymous:
        post['username'] = board_content.is_anonymous
    post['return'] = (userprofile == request.user.userprofile)
    post['is_anonymous'] = board_content.is_anonymous
    post['vote'] = board_content.get_vote()
    post['vote']['is_up'] = False
    post['vote']['is_down'] = False
    if target_type == 'Comment':
        post['board_comment'] = board_content.board_comment
    if board_content.use_signiture:
        post['signiture'] = request.user.userprofile.signiture
    else:
        post['signiture'] = ''
    try:
        is_vote = BoardContentVote.objects.get(
            userprofile=userprofile, board_content=board_content)
        if is_vote.is_up:
            post['vote']['is_up'] = True
        else:
            post['vote']['is_down'] = True
    except ObjectDoesNotExist:
        pass
    post['adult'] = board_content.is_adult
    return post


def _write_post(request, is_modify=False, post=None,
                content=None, board="All"):
    form_content = BoardContentForm(
        request.POST,
        instance=content,
        is_modify=is_modify,
        author=request.user.userprofile)
    form_post = BoardPostForm(
        request.POST,
        instance=post,
        is_staff=request.user.is_staff)  # get form from post and instance
    form_attachment = AttachmentFormSet(request.POST, request.FILES)
    # Get board instance, if failed return fail
    try:
        board_instance = Board.objects.get(url=board)
    except:
        return {'failed': [form_content, form_post, form_attachment]}
    try:  # for modify log, get title and content before modify.
        # modify log for content
        content_before = content.content
        # modify log for post
        title_before = post.title
        board_before = post.board.kor_name
        category_before = post.board_category.name
    except:  # no such a content : is not modify
        category_before = ""
    if (form_post.is_valid() and form_content.is_valid()
            and form_attachment.is_valid()):
        images = imtag_regex.findall((form_content.cleaned_data['content']))
        images = iri_to_uri(','.join(images))
        images = images.split(iri_to_uri(','))
        if is_modify:
            try:
                category_after = post.board_category.name
            except:
                category_after = ""
            content_diff = [[str(content.modified_time),
                             _get_diff_match(content_before, content.content)]]
            if board_before == post.board.kor_name:
                board_diff = [[0, board_before]]
            else:
                board_diff = [[-1, board_before], [1, post.board.kor_name]]
            if category_before == category_after:
                category_diff = [[0, category_before]]
            else:
                category_diff = [[-1, category_before], [1, category_after]]
            post_diff = [[_get_diff_match(title_before, post.title),
                          board_diff,
                          category_diff]]
            post.set_log(post_diff + post.get_log())
            content.set_log(content_diff + content.get_log())
            # 위지윅으로 저장된 이미지들 확인
            stored_image = Attachment.objects.filter(board_content=content)
            delete_list = list(stored_image)
            for image in stored_image:
                name = image.file.url
                if name in images:
                    images.remove(name)
                    delete_list.remove(image)
            # 삭제된 이미지 클래스 삭제하기
            for image in delete_list:
                if image.file:
                    if os.path.isfile(image.file.path):
                        os.remove(image.file.path)
                image.delete()
        else:
            request.user.userprofile.points += POINTS_POST_WRITE
            request.user.userprofile.save()
        board_post = form_post.save(
            author=request.user.userprofile,
            content=form_content.save(post=post),
            board=board_instance)  # save
        board_content = board_post.board_content
        board_name = board_post.board.eng_name
        HashTag.objects.filter(board_post=board_post).delete()
        hashs = board_content.get_hashtags()
        # 위지윅으로 업로드 된 이미지 처리
        content = board_content.content
        for img_src in images:
            if len(img_src) == 0:
                continue
            src = img_src.split(urlquote('/'))[-1]
            path_origin = uri_to_iri(default_storage.path(uri_to_iri(src)))
            with open(path_origin, "r") as file_origin:
                file_content = ContentFile(file_origin.read())
                attachment = Attachment(board_content=board_content)
                new_path = '/'.join([board_name,
                                     str(board_post.id),
                                     path_origin.split('/')[-1]])
                attachment.file.save(new_path, file_content)
                attachment.save()
            if file_origin.closed:
                os.remove(unicode(file_origin.name))
                del file_origin
            content = content.replace(src, attachment.file.name)
        # Delete all django summernote attachment models
        summernote.Attachment.objects.all().delete()
        board_content.content = content
        board_content.save()
        for tag in hashs:
            HashTag(tag_name=tag, board_post=board_post).save()
        attachments = form_attachment.save(commit=False)
        # 삭제 항목에 체크 된 항목들 삭제
        for attachment in form_attachment.deleted_objects:
            attachment.delete()
        for attachment in attachments:
            attachment.board_content = board_content
            attachment.save()
        return {'save': board_post}
    else:
        return {'failed': [form_content, form_post, form_attachment]}


def _write_comment(request, post_id, is_modify=False):
    user_profile = request.user.userprofile
    if is_modify:
        comment_id = request.POST.get('board_comment_id', 0)
        try:
            board_comment = BoardComment.objects.get(id=comment_id)
            content_before = board_comment.board_content.content
            form_attachment = AttachmentFormSet(
                queryset=Attachment.objects.none())
            if (board_comment.author != user_profile
                    and user_profile.permission < 4):
                return  # wrong request
            content_form = BoardContentForm(
                request.POST,
                instance=board_comment.board_content,
                is_modify=True,
                author=request.user.userprofile)
        except ObjectDoesNotExist:
            return  # no comment
    else:
        form_attachment = AttachmentFormSet(request.POST, request.FILES)
        target_post = BoardPost.objects.get(id=post_id)
        try:
            board_comment = BoardComment(
                author=user_profile,
                board_post=target_post)
            content_form = BoardContentForm(request.POST,
                                            author=request.user.userprofile)
        except:
            return  # no post
    if content_form.is_valid():
        if is_modify:
            board_comment.board_content.set_log(
                [[str(board_comment.board_content.modified_time),
                  _get_diff_match(content_before,
                                  board_comment.board_content.content)]] +
                board_comment.board_content.get_log())
        else:
            request.user.userprofile.points += POINTS_COMMENT_WRITE
            request.user.userprofile.save()
        board_comment.board_content = content_form.save(
            post=board_comment.board_post)
    else:
        return  # Invalid form
        board_comment.board_content = content_form.save(
            post=board_comment.board_post)
    '''
    if form_attachment.is_valid():
        attachments = form_attachment.save(commit=False)
        for attachment in attachments:
            attachment.board_content = board_comment.board_content
            attachment.save()
    '''
    board_comment.board_post.board_content.save()  # update modified_time
    board_comment.save()
    notify_target = board_comment.board_post.get_notify_target()

    for target in notify_target:
        target = target.userprofile.user
        if request.user != target:
            notify.send(request.user,
                        recipient=target,
                        verb='가 댓글을 달았습니다.'.decode('utf-8'),
                        post_title=target_post.title,
                        comment_content=board_comment.board_content.content,
                        board_name=target_post.board.url,
                        noti_category='reply',
                        app_title='board',
                        post_id=target_post.id,
                        comment_page=1)
    numtags = board_comment.board_content.get_numtags()
    if numtags:
        comments = board_comment.board_post.board_comment.all()
        comments = comments.order_by('id')
        for num in numtags:
            try:
                if num == 0:
                    notify.send(request.user,
                                recipient=board_comment.board_post.author.user,
                                verb='님이 태그했습니다.'.decode('utf-8'),
                                post_title=board_comment.board_content.content,
                                # post_title=target_post.title,
                                # comment_content=board_comment.board_content.content,
                                board_name=target_post.board.url,
                                noti_category='mention',
                                app_title='board',
                                post_id=target_post.id,
                                comment_page=1)
                else:
                    target = comments[num - 1].author.user
                    notify.send(request.user,
                                recipient=target,
                                verb='님이 태그했습니다.'.decode('utf-8'),
                                post_title=board_comment.board_content.content,
                                # post_title=target_post.title,
                                # comment_content=board_comment.board_content.content,
                                board_name=target_post.board.url,
                                noti_category='mention',
                                app_title='board',
                                post_id=target_post.id,
                                comment_page=1)
            except:
                pass
    comment_list = []
    comment_nickname_list = []
    if board_comment.board_post.board_content.is_anonymous is None:
        comment_nickname_list = [(board_comment.board_post.author.nickname, 0)]
    order = 1
    for board_comment in board_comment.board_post.board_comment.all():
        comment = _get_post(request, board_comment, 'Comment',
                            comment_nickname_list)
        comment_list.append(board_comment)
        # 현재 글에 달린 댓글의 닉네임 리스트
        if comment['is_anonymous'] is None:
            username = comment['username']
            comment_nickname_list.append((username, order))
        order = order + 1
    orders = board_comment.board_content.get_taged_order(comment_nickname_list)
    for order in orders:
        order = order - 1
        if order == -1:
            target = board_comment.board_post.author.user
        else:
            target = comment_list[order].author.user
        if request.user != target:
            notify.send(request.user,
                        recipient=target,
                        verb='님이 태그했습니다.'.decode('utf-8'),
                        post_title=board_comment.board_content.content,
                        # post_title=target_post.title,
                        # comment_content=board_comment.board_content.content,
                        board_name=target_post.board.url,
                        noti_category='mention',
                        app_title='board',
                        post_id=target_post.id,
                        comment_page=1)
    return board_comment.board_post.id, order - 1


def _delete_post(request):
    # message = ''
    board_content_id = request.POST.get('id', 0)
    try:
        board_content = BoardContent.objects.get(id=board_content_id)
    except ObjectDoesNotExist:
        return 'no post or comment'
    if hasattr(board_content, 'board_post'):
        author = board_content.board_post.author
    elif hasattr(board_content, 'board_comment'):
        author = board_content.board_comment.author
    else:
        return 'invalid content'
    if (author != request.user.userprofile
            and request.user.userprofile.permission < 4):
        return 'not allowed'
    board_content.is_deleted = True
    board_content.save()
    request.user.userprofile.points += POINTS_POST_DELETE
    request.user.userprofile.save()
    return 'success'


def _report(request):
    content_id = request.POST.get('id', 0)
    report_form = BoardReportForm(request.POST)
    if report_form.is_valid():
        try:
            board_content = BoardContent.objects.get(id=content_id)
        except:
            return {'message': 'No content'}
        report_form.save(user=request.user.userprofile,
                         content=board_content)
        return {'message': 'Success'}
    else:
        return {'message': 'Invalid form'}


def _vote(request):
    cancel = ''
    user_profile = request.user.userprofile
    vote_type = request.POST.get('vote_type', '')
    content_id = request.POST.get('vote_id', '')
    try:
        board_content = BoardContent.objects.get(id=content_id)
        if vote_type == 'up' or vote_type == 'down':
            is_up_or_down = (False, True)[vote_type == 'up']
            try:
                content_vote = BoardContentVote.objects.get(
                    board_content=board_content,
                    userprofile=user_profile)
                if content_vote.is_up == is_up_or_down:
                    content_vote.delete()
                    if is_up_or_down:
                        points = POINTS_VOTED_UP
                    else:
                        points = POINTS_VOTED_DOWN
                        user_profile.points -= POINTS_VOTE_DOWN
                        user_profile.save()
                    if hasattr(board_content, 'board_post'):
                        board_content.board_post.author.points -= points
                        board_content.board_post.author.save()
                    else:
                        board_content.board_comment.author.points -= points
                        board_content.board_comment.author.save()
                    return {'success': vote_type + ' canceled',
                            'vote': board_content.get_vote(), 'cancel': 'yes'}
                else:
                    content_vote.is_up = is_up_or_down
                    content_vote.save()
                    _make_best(board_content)
                    if is_up_or_down:
                        points = POINTS_VOTED_UP - POINTS_VOTED_DOWN
                        user_profile.points -= POINTS_VOTE_DOWN
                        user_profile.save()
                    else:
                        points = POINTS_VOTED_DOWN - POINTS_VOTED_UP
                        user_profile.points += POINTS_VOTE_DOWN
                        user_profile.save()
                    if hasattr(board_content, 'board_post'):
                        board_content.board_post.author.points += points
                        board_content.board_post.author.save()
                    else:
                        board_content.board_comment.author.points += points
                        board_content.board_comment.author.save()
                    return {'success': 'changed to ' + vote_type,
                            'vote': board_content.get_vote(), 'cancel': 'no'}
            except:
                cancel = 'no'
                vote = BoardContentVote()
                vote.is_up = is_up_or_down
                if is_up_or_down:
                    points = POINTS_VOTED_UP
                else:
                    points = POINTS_VOTED_DOWN
                    user_profile.points += POINTS_VOTE_DOWN
                    user_profile.save()
                if hasattr(board_content, 'board_post'):
                    board_content.board_post.author.points += points
                    board_content.board_post.author.save()
                else:
                    board_content.board_comment.author.points += points
                    board_content.board_comment.author.save()
        elif vote_type == 'adult':
            if BoardContentVoteAdult.objects.filter(
                    board_content=board_content,
                    userprofile=user_profile):
                return {'success': 'Already voted ' + vote_type,
                        'vote': board_content.get_vote(), 'cancel': cancel}
            else:
                vote = BoardContentVoteAdult()
        elif vote_type == 'political':
            if BoardContentVotePolitical.objects.filter(
                    board_content=board_content,
                    userprofile=user_profile):
                return {'success': 'Already voted ' + vote_type,
                        'vote': board_content.get_vote(), 'cancel': cancel}
            else:
                vote = BoardContentVotePolitical()
        else:
            return {'fail': 'Wrong request'}
        vote.board_content = board_content
        vote.userprofile = user_profile
        vote.save()
        _make_best(board_content)
        return {'success': 'vote ' + vote_type,
                'vote': board_content.get_vote(), 'cancel': cancel}
    except ObjectDoesNotExist:
        return {'fail': 'Unvalid ontent id'}


def _make_best(board_content):
    if hasattr(board_content, 'board_post'):
        board_post = board_content.board_post
        vote = board_content.get_vote()
        if vote['up'] > 0 and board_post.is_best is False:
            board_post.is_best = True
            board_post.save()
            return True
    return False


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
    board_post = BoardPost.objects.filter(id=post_id)[0]
    board_content = board_post.board_content
    post = [board_post.title,
            board_post.board.kor_name,
            board_post.board_category,
            board_content.modified_time,
            board_content.content]
    modify_log = []
    for log_post, log_content in izip(board_post.get_log(),
                                      board_content.get_log()):
        modify_log = modify_log +\
            [[diff_obj.diff_prettyHtml(log_post[0]),
              diff_obj.diff_prettyHtml(log_post[1]),
              diff_obj.diff_prettyHtml(log_post[2]),
              log_content[0],
              diff_obj.diff_prettyHtml(log_content[1])]]
    return post, modify_log


def _get_comment_log(comment_id):
    diff_obj = diff_match_patch.diff_match_patch()
    board_comment = BoardComment.objects.filter(id=comment_id)[0]
    board_content = board_comment.board_content
    comment = [board_content.modified_time,
               board_content.content]
    modify_log = []
    for log_content in board_content.get_log():
        modify_log = modify_log +\
            [[log_content[0], diff_obj.diff_prettyHtml(log_content[1])]]
    return comment, modify_log


def _create_board(request):
    form_board = BoardForm(request.POST)
    if form_board.is_valid():
        board = form_board.save(admin=request.user.userprofile)
        return {'save': board}
    return {'failed': form_board}


def _remove_board(request, board_url):
    try:
        board = Board.objects.get(url=board_url)
        if board.is_deleted:
            return 'already deleted'
        if board.admin == request.user.userprofile:
            board.is_deleted = True
            board.save()
            return 'success'
        return 'not allowed'
    except:
        return 'invaid access'


def _add_member(request, board):
    member_name = request.POST.get('member', '')
    form_boardmember = BoardMemberForm(request.POST,
                                       board=board)
    if form_boardmember.is_valid():
        boardmember = form_boardmember.save()
        return {'save': boardmember}
    return {'failed': form_boardmember}


def _change_permission(request, board):
    for nickname, permission in request.POST.iteritems():
        try:
            member = BoardMember.objects.get(board=board,
                                             member__nickname=nickname)
        except:
            continue
        write = False
        if permission == 'on':
            write = True
        if member.write != write:
            member.write = write
            member.save()


def _check_valid(request, board_url, write=False):
    if board_url.lower() in ['all', 'garbage']:
        return True
    try:
        board = Board.objects.get(url=board_url)
    except:
        return False
    if board.is_deleted:
        return False
    if board.is_public:
        return True
    if request.user.userprofile.permission > 3:
        return True
    if board.admin == request.user.userprofile:
        return True
    try:
        board_member = BoardMember.objects.get(
            board=board, member=request.user.userprofile)
        return not (write and not board_member.write)
    except:
        return False
