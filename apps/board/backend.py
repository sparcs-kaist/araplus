# -*- coding: utf-8
from apps.board.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import diff_match_patch
from django.db.models import Q
from apps.board.forms import *
from itertools import izip


POINTS_POST_WRITE = 5
POINTS_COMMENT_WRITE = 3
POINTS_POST_DELETE = -5
POINTS_VOTED_UP = 3
POINTS_VOTE_DOWN = -1
POINTS_VOTED_DOWN = -2


def _get_post_list(request, board_url='', item_per_page=15):
    adult_filter = request.GET.get('adult_filter')
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
    if board_url == 'all':
        board_post_notice = BoardPost.objects.filter(is_notice=True,
                                                     board__is_deleted=False,
                                                     board__is_official=True)
        board_post = BoardPost.objects.filter(board__is_deleted=False,
                                              board__is_official=True)
    else:
        board_post_notice = BoardPost.objects.filter(is_notice=True,
                                                     board=board)
        board_post = BoardPost.objects.filter(board=board)
    # search
    if best_filter:
        board_post = board_post.filter(is_best=True)
    if search_tag:
        board_post = board_post.filter(hashtag__tag_name=search_tag)
    if search_title:
        board_post = board_post.filter(title__contains=search_title)
    if search_content:
        board_post = board_post.filter(
            Q(board_content__content__contains=search_content)
            | Q(title__contains=search_content))
    if search_nickname:
        board_post = board_post.filter(author__nickname=search_nickname,
                                       board_content__is_anonymous=None)
    if search_category:
        board_post = board_post.filter(board_category__name=search_category)
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


def _get_content(request, post_id):
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
    except ObjectDoesNotExist:
        board_post_is_read = BoardPostIs_read()
        board_post_is_read.board_post = board_post
        board_post_is_read.userprofile = request.user.userprofile
    board_post_is_read.save()
    post = _get_post(request, board_post, 'Post')
    comment_list = []
    comment_nickname_list = []
    order = 1
    for board_comment in board_post.board_comment.all():
        comment = _get_post(request, board_comment, 'Comment',
                            comment_nickname_list)
        comment['order'] = order
        order = order + 1
        comment['is_political'] = board_comment.is_political
        comment_list.append(comment)
        # 현재 글에 달린 댓글의 닉네임 리스트
        username = comment['username']
        if order == 2:
            comment_nickname_list.append((username, 1))
        else:
            n = len(comment_nickname_list)
            x = n
            y = n
            for i in range(0, n):
                if comment_nickname_list[i][0] == username:
                    x = i
                    y = i + 1
                    break
                if (len(username) >= len(comment_nickname_list[i][0])
                        and x == n):
                    x = i
                    y = i
            comment_nickname_list = comment_nickname_list[0:x] + [(username, order-1)] + comment_nickname_list[y:]
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


def _get_post(request, board_post, type, comment_nickname_list=[]):
    post = {}
    if type == 'Comment':
        pass
    elif type == 'Post':
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
            type, comment_nickname_list)
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
        instance=post)  # get form from post and instance
    form_attachment = AttachmentFormSet(request.POST, request.FILES)
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
        else:
            request.user.userprofile.points += POINTS_POST_WRITE
            request.user.userprofile.save()
        board_post = form_post.save(
            author=request.user.userprofile,
            content=form_content.save(post=post))  # save
        board_content = board_post.board_content
        HashTag.objects.filter(board_post=board_post).delete()
        hashs = board_content.get_hashtags()
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
            if board_comment.author != user_profile:
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
        try:
            board_comment = BoardComment(
                author=user_profile,
                board_post=BoardPost.objects.get(id=post_id))
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
    if form_attachment.is_valid():
        attachments = form_attachment.save(commit=False)
        for attachment in attachments:
            attachment.board_content = board_comment.board_content
            attachment.save()
    board_comment.board_post.board_content.save()  # update modified_time
    board_comment.save()
    print board_comment.board_post.id
    return board_comment.board_post.id


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
    if author != request.user.userprofile:
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
        if board_content.go_political():
            try:
            board_post = BoardPost.objects.get(board_content=board_content)
            board_political = Board.objects.get(eng_name='Political')
            board_post.board = board_political
            board_post.save()
            except ObjectDoesNotExits:
                board_comment = BoardComment.objects.get(board_content=board_content)
                board_political = Board.objects.get(eng_name='Political')
                board_comment.save()
            if board_content.go_adult():
                board_content.is_adult = True
                board_content.save()
        return {'success': 'vote ' + vote_type,
                'vote': board_content.get_vote(), 'cancel': cancel}
    except ObjectDoesNotExist:
        return {'fail': 'Unvalid content id'}


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


def _check_valid(request, board_url, write=False):
    if board_url.lower() == 'all':
        return True
    try:
        board = Board.objects.get(url=board_url)
    except:
        return False
    if board.is_deleted:
        return False
    if board.is_public:
        return True
    if board.admin == request.user.userprofile:
        return True
    try:
        board_member = BoardMember.objects.get(
            board=board, member=request.user.userprofile)
        if write and not board_member.write:
            return False
        return True
    except:
        pass
    return False
