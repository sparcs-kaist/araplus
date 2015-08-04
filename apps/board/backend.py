# -*- coding: utf-8
from apps.board.models import *
from django.core.exceptions import ObjectDoesNotExist
import diff_match_patch
from django.db.models import Q
from apps.board.forms import *


def _get_post_list(request, board_url='', item_per_page=15):
    adult_filter = request.GET.get('adult_filter')
    best_filter = request.GET.get('best', '')
    search_title = request.GET.get('title', '')
    search_content = request.GET.get('content', '')  # title + content
    search_nickname = request.GET.get('nickname', '')

    try:
        page = int(request.GET['page'])
    except:
        page = 1
    if board_url != 'all':
        try:
            board = Board.objects.get(name=board_url)
        except:
            return ([], [])
    post_count = 0
    if board_url == 'all':
        board_post_notice = BoardPost.objects.filter(
            is_notice=True).order_by('-id')
        if best_filter == 'true':
            board_post = BoardPost.objects.filter(is_best=True).order_by('-id')
        else:
            board_post = BoardPost.objects.all().order_by('-id')
    else:
        board_post_notice = BoardPost.objects.filter(
            is_notice=True, board=board).order_by('-id')
        if best_filter == 'true':
            board_post = BoardPost.objects.filter(
                board=board, is_best=True).order_by('-id')
        else:
            board_post = BoardPost.objects.filter(
                board=board).order_by('-id')
    if search_title:
        board_post = board_post.filter(title__contains=search_title)
    if search_content:
        board_post = board_post.filter(
            Q(board_content__content__contains=search_content)
            | Q(title__contains=search_content))
    if search_nickname:
        board_post = board_post.filter(author__nickname=search_nickname,
                                       board_content__is_anonymous=None)
    post_count = board_post.count()
    if post_count == 0:
        post_count = 1
    last_page = (post_count - 1) / item_per_page + 1
    if page < 1:
        page = 1
    elif page > last_page:
        page = last_page
    board_post_notice = board_post_notice[:5]
    board_post_all = board_post[
        (page * item_per_page - item_per_page):(page * item_per_page)]
    post_list = []
    for board_post in board_post_notice:
        post = {}
        if board_post.is_notice:
            if board_post.board_content.is_deleted:
                continue
            post['is_notice'] = True
        if board_post.board_content.is_anonymous:
            post['username'] = board_post.board_content.is_anonymous
        else:
            post['username'] = board_post.author.nickname
        post_board = {}
        post_board['board_name'] = board_post.board.name
        post_board['board_url'] = board_post.board.name
        post['board'] = post_board
        post['title'] = board_post.title
        post['created_time'] = board_post.board_content.created_time
        post['post_id'] = board_post.id
        post['vote'] = board_post.board_content.get_vote()
        post['comment_count'] = board_post.board_comment.count()
        if adult_filter == 'true' and board_post.board_content.is_adult:
            post['title'] = 'filtered'
        try:
            is_read = BoardPostIs_read.objects.get(
                board_post=board_post,
                userprofile=request.user.userprofile)
            if is_read.last_read > board_post.board_content.modified_time:
                post['is_read'] = ' '
            else:
                post['is_read'] = 'U'
        except ObjectDoesNotExist:
            post['is_read'] = 'N'
        post_list.append(post)
    for board_post in board_post_all:
        post = {}
        post['is_notice'] = False
        if board_post.board_content.is_anonymous:
            post['username'] = board_post.board_content.is_anonymous
        else:
            post['username'] = board_post.author.nickname
        post_board = {}
        post_board['board_name'] = board_post.board.name
        post_board['board_url'] = board_post.board.name
        post['board'] = post_board
        post['title'] = board_post.title
        post['created_time'] = board_post.board_content.created_time
        post['post_id'] = board_post.id
        post['vote'] = board_post.board_content.get_vote()
        post['comment_count'] = board_post.board_comment.count()
        post['is_best'] = board_post.is_best
        if adult_filter == 'true' and board_post.board_content.is_adult:
            post['title'] = 'filtered'
        if board_post.board_content.is_deleted:
            post['title'] = '--Deleted--'
        try:
            is_read = BoardPostIs_read.objects.get(
                board_post=board_post,
                userprofile=request.user.userprofile)
            if is_read.last_read > board_post.board_content.modified_time:
                post['is_read'] = ' '
            else:
                post['is_read'] = 'U'
        except ObjectDoesNotExist:
            post['is_read'] = 'N'
        post_list.append(post)
    paginator = []
    if page > 10:
        paging = {}
        paging['page'] = 'prev'
        paging['url'] = str((page - page % 10))
        paginator.append(paging)
    for i in range(page - (page - 1) % 10, page - (page - 1) % 10 + 10):
        if i > last_page:
            break
        paging = {}
        paging['page'] = str(i)
        paging['url'] = str(i)
        paginator.append(paging)
        if page < last_page - (last_page - 1) % 10:
            paging = {}
            paging['page'] = 'next'
            paging['url'] = str((page - (page - 1) % 10 + 10))
            paginator.append(paging)
        return (post_list, paginator)


def _get_board_list():
    board_model_list = Board.objects.all()
    board_list = []
    for board_model in board_model_list:
        board = {}
        board['board_name'] = board_model.name
        board['board_url'] = board_model.name
        board['board_id'] = board_model.id
        board_list.append(board)
    return board_list


def _get_current_board(request, board_url):
    board = {}
    try:
        board_model = Board.objects.get(name=board_url)
        board['board_id'] = board_model.id
        board['board_name'] = board_model.name
        board['board_url'] = board_model.name
    except:
        pass
    if request.GET.get('best', '') == 'true':
        board['best'] = True
    return board


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
    for board_comment in board_post.board_comment.all():
        comment = _get_post(request, board_comment, 'Comment')
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


def _get_post(request, board_post, type):
    post = {}
    if type == 'Comment' or type == 'Re-Comment':
        pass
    elif type == 'Post':
        post['title'] = board_post.title
        post['board'] = board_post.board.name
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
        post['content'] = board_content.content
    post['id'] = board_post.id
    post['deleted'] = board_content.is_deleted
    post['content_id'] = board_content.id
    post['created_time'] = board_content.created_time
    post['username'] = userprofile.nickname
    if board_content.is_anonymous:
        post['username'] = board_content.is_anonymous
    post['return'] = (userprofile == request.user.userprofile)
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
        is_modify=is_modify)
    form_post = BoardPostForm(
        request.POST,
        instance=post)  # get form from post and instance
    try:  # for modify log, get title and content before modify.
        # modify log for content
        content_before = content.content
        # modify log for post
        title_before = post.title
        board_before = post.board.name
        category_before = post.board_category.name
    except:  # no such a content : is not modify
        category_before = ""
    if form_post.is_valid() and form_content.is_valid():
        if is_modify:
            try:
                category_after = post.board_category.name
            except:
                category_after = ""
            content_diff = [[str(content.modified_time),
                             _get_diff_match(content_before, content.content)]]
            if board_before == post.board.name:
                board_diff = [[0, board_before]]
            else:
                board_diff = [[-1, board_before], [1, post.board.name]]
            if category_before == category_after:
                category_diff = [[0, category_before]]
            else:
                category_diff = [[-1, category_before], [1, category_after]]
            post_diff = [[_get_diff_match(title_before, post.title),
                          board_diff,
                          category_diff]]
            post.set_log(post_diff + post.get_log())
            content.set_log(content_diff + content.get_log())
        board_post = form_post.save(
            author=request.user.userprofile,
            content=form_content.save(author=request.user.userprofile,
                                      post=post))  # save
        return {'save': board_post}
    else:
        return {'failed': [form_content, form_post]}


def _write_comment(request, post_id, is_modify=False):
    user_profile = request.user.userprofile
    if is_modify:
        comment_id = request.POST.get('board_comment_id', 0)
        try:
            board_comment = BoardComment.objects.get(id=comment_id)
            content_before = board_comment.board_content.content
            if board_comment.author != user_profile:
                return  # wrong request
            content_form = BoardContentForm(
                request.POST,
                instance=board_comment.board_content,
                is_modify=True)
        except ObjectDoesNotExist:
            return  # no comment
    else:
        try:
            board_comment = BoardComment(
                author=user_profile,
                board_post=BoardPost.objects.get(id=post_id))
            content_form = BoardContentForm(request.POST)
        except:
            return  # no post
    if content_form.is_valid():
        if is_modify:
            board_comment.board_content.set_log(
                [[str(board_comment.board_content.modified_time),
                  _get_diff_match(content_before,
                                  board_comment.board_content.content)]] +
                board_comment.board_content.get_log())
        board_comment.board_content = content_form.save(
            author=user_profile,
            post=board_comment.board_post)
    else:
        return  # Invalid form
        board_comment.board_content = content_form.save(
            author=user_profile,
            post=board_comment.board_post)
    board_comment.save()
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
    return 'success'


def _report(request):
    content_id = request.POST.get('id', 0)
    report_form = BoardReportForm(request.POST)
    print report_form.errors
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
                    return {'success': vote_type + ' canceled',
                            'vote': board_content.get_vote(), 'cancel': 'yes'}
                else:
                    content_vote.is_up = is_up_or_down
                    content_vote.save()
                    _make_best(board_content)
                    return {'success': 'changed to ' + vote_type,
                            'vote': board_content.get_vote(), 'cancel': 'no'}
            except:
                cancel = 'no'
                vote = BoardContentVote()
                vote.is_up = is_up_or_down
        elif vote_type == 'adult':
            if BoardContentVoteAdult.objects.filter(
                    board_content=board_content,
                    userprofile=user_profile):
                return {'success': 'Already voted' + vote_type,
                        'vote': board_content.get_vote()}
            else:
                vote = BoardContentVoteAdult()
        elif vote_type == 'political':
            if BoardContentVotePolitical.objects.filter(
                    board_content=board_content,
                    userprofile=user_profile):
                return {'success': 'Already voted ' + vote_type,
                        'vote': board_content.get_vote()}
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
