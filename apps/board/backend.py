# -*- coding: utf-8
from apps.board.models import *
import datetime


def _get_post_list(request, item_per_page=15):
    adult_filter = request.GET.get('adult_filter')
    board_filter = request.GET.get('board')
    try:
        page = int(request.GET['page'])
    except:
        page = 1
    board_querystring = ''
    if board_filter:
        board = Board.objects.filter(id=board_filter)
        if board:
            board = board[0]
        else:
            return ([], [])
        board_querystring = 'board='+str(board.id)
    post_count = 0
    if board_filter:
        board_post_notice = BoardPost.objects.filter(is_notice=True, board=board_filter).order_by('-id')
        board_post = BoardPost.objects.filter(board=board_filter).order_by('-id')
        post_count = board.post_count
    else:
        board_post_notice = BoardPost.objects.filter(is_notice=True).order_by('-id')
        board_post = BoardPost.objects.filter(is_notice=False).order_by('-id')
        for board in Board.objects.all():
            post_count += board.post_count
    if post_count == 0:
        post_count = 1
    last_page = (post_count-1)/item_per_page+1
    if page < 1:
        page = 1
    elif page > last_page:
        page = last_page
    board_post_notice = board_post_notice[:5]
    board_post_all = board_post[(page*item_per_page-item_per_page):(page*item_per_page)]
    post_list = []
    for board_post in board_post_notice:
        post = {}
        if board_post.is_notice:
            if board_post.board_content.is_deleted:
                continue
            post['is_notice'] = True
        if board_post.board_content.is_anonymous:
            post['username'] = 'anonymous'
        else:
            post['username'] = board_post.author.user.username
        post_board = {}
        post_board['board_name'] = board_post.board.name
        post_board['querystring'] = '?board='+str(board_post.board.id)
        post['board'] = post_board
        post['title'] = board_post.title
        post['created_time'] = board_post.board_content.created_time
        post['post_id'] = board_post.id
        post['vote'] = board_post.board_content.get_vote()
        if adult_filter == 'true' and board_post.board_content.is_adult:
            post['title'] = 'filtered'
        post_list.append(post)
    for board_post in board_post_all:
        post = {}
        post['is_notice'] = False
        if board_post.board_content.is_anonymous:
            post['username'] = 'anonymous'
        else:
            post['username'] = board_post.author.user.username
        post_board = {}
        post_board['board_name'] = board_post.board.name
        post_board['querystring'] = '?board='+str(board_post.board.id)
        post['board'] = post_board
        post['title'] = board_post.title
        post['created_time'] = board_post.board_content.created_time
        post['post_id'] = board_post.id
        post['vote'] = board_post.board_content.get_vote()
        if adult_filter == 'true' and board_post.board_content.is_adult:
            post['title'] = 'filtered'
        post_list.append(post)
    paginator = []
    if page > 10:
        paging = {}
        paging['page'] = 'prev'
        if board_querystring:
            paging['querystring'] = '?'+board_querystring+'&page='+str((page-page % 10))
        else:
            paging['querystring'] = '?page='+str((page-page % 10))
        paginator.append(paging)
    for i in range(page-(page-1) % 10, page-(page-1) % 10+10):
        if i > last_page:
            break
        paging = {}
        paging['page'] = str(i)
        if board_querystring:
            paging['querystring'] = '?'+board_querystring+'&page='+str(i)
        else:
            paging['querystring'] = '?page='+str(i)
        paginator.append(paging)
    if page < last_page-(last_page-1) % 10:
        paging = {}
        paging['page'] = 'next'
        if board_querystring:
            paging['querystring'] = '?'+board_querystring+'&page='+str((page-(page-1) % 10+10))
        else:
            paging['querystring'] = '?page='+str((page-(page-1) % 10+10))
        paginator.append(paging)
    return (post_list, paginator)


def _get_board_list():
    board_model_list = Board.objects.all()
    board_list = []
    for board_model in board_model_list:
        board = {}
        board['board_name'] = board_model.name
        board['querystring'] = '?board='+str(board_model.id)
        board['board_id'] = board_model.id
        board_list.append(board)
    return board_list


def _get_current_board(request):
    board = {}
    try:
        board_model = Board.objects.filter(id=request.GET.get('board'))[0]
        board['board_id'] = board_model.id
        board['board_name'] = board_model.name
        board['querystring'] = '?board='+str(board_model.id)
    except:
        board['board_id'] = None
        board['board_name'] = None
    return board


def _get_querystring(request):
    querystring = ''
    board_filter = request.GET.get('board')
    page = request.GET.get('page')
    if board_filter or page:
        querystring = '?'
        if board_filter:
            querystring += 'board='+board_filter
            if page:
                querystring += '&page='+page
        else:
            querystring += 'page='+page
    return querystring


def _get_content(request, post_id):
    board_post = BoardPost.objects.filter(id=post_id)
    if board_post:
        board_post = board_post[0]
    else:
        return (_get_post(request, 0), [])
    post = _get_post(request, board_post.board_content)
    comment_list = []
    for board_comment in board_post.board_comment.all():
        comment = _get_post(request, board_comment.board_content, True)
        comment_list.append(comment)
    return (post, comment_list)


def _get_post(request, board_content, is_comment=False):
    post = {}
    if is_comment:
        board_post = board_content.board_comment
    else:
        board_post = board_content.board_post
        post['title'] = board_post.title
        post['board'] = board_post.board.name
        post['board_id'] = board_post.board.id
        post['category'] = board_post.board_category.name
    userprofile = board_post.author
    user = userprofile.user
    if board_content.is_deleted:
        post['title'] = '--Deleted--'
        post['content'] = '--Deleted--'
    else:
        post['content'] = board_content.content
    post['id'] = board_post.id
    post['deleted'] = board_content.is_deleted
    post['content_id'] = board_content.id
    post['created_time'] = board_content.created_time
    post['username'] = user.username
    if board_content.is_anonymous:
        post['username'] = 'anonymous'
    post['return'] = (user.id == request.user.id)
    post['vote'] = board_content.get_vote()
    post['adult'] = board_content.is_adult
    return post


def _write_post(request, is_post_or_comment, check=0, modify=False):
    user_profile = request.user.userprofile
    content = request.POST.get('content', '')
    is_anonymous = request.POST.get('anonymous', False)
    is_adult = request.POST.get('adult', False)
    if modify:
        try:
            if is_post_or_comment == 'Post':
                board_post_id = int(request.POST.get('board_post_id', 0))
                board_post = BoardPost.objects.filter(id=board_post_id)[0]
                board_content = board_post.board_content
                author = board_post.author
            elif is_post_or_comment == 'Comment':
                board_comment_id = int(request.POST.get('board_comment_id', 0))
                board_comment = BoardComment.objects.filter(id=board_comment_id)[0]
                board_content = board_comment.board_content
                author = board_comment.author
            else:
                return
        except:
            return
        if author != user_profile:
            return
        if board_content.is_deleted:
            return
    else:
        board_content = BoardContent()
    if not content:
        return
    board_content.content = content
    board_content.is_adult = bool(is_adult)
    if not modify:
        board_content.is_anonymous = bool(is_anonymous)
        board_content.created_time = datetime.datetime.today()
    if is_post_or_comment == 'Post':
        board = request.POST.get('board', 0)
        is_notice = request.POST.get('notice', False)
        category = request.POST.get('category', 0)
        title = request.POST.get('title', '')
        if modify:
            board_post = board_content.board_post
        else:
            board_post = BoardPost()
        try:
            board_post.board = Board.objects.filter(id=board)[0]
            board_post.board_category = BoardCategory.objects.filter(name=category, board=board_post.board)[0]
        except IndexError:
            return
        board_content.save()
        board_post.board_content = board_content
        board_post.is_notice = bool(is_notice)
        board_post.author = user_profile
        board_post.title = title
        board_post.save()
        if not modify:
            board_post.board.post_count += 1
            board_post.board.save()
        return board_post.id
    elif is_post_or_comment == 'Comment':
        board_post_id = request.POST.get('board_post_id', 0)
        if not check == board_post_id:
            print 'not allowed'
            return
        if modify:
            try:
                board_comment_id = request.POST.get('board_comment_id', 0)
                board_comment = BoardComment.objects.filter(id=board_comment_id)[0]
            except:
                return
        else:
            board_comment = BoardComment()
            try:
                board_comment.board_post = BoardPost.objects.filter(id=board_post_id)[0]
            except IndexError:
                return
        board_comment.author = user_profile
        board_content.save()
        board_comment.board_content = board_content
        board_comment.save()
        return board_comment.board_post.id
    else:
        return
