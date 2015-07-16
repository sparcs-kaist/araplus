# -*- coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from apps.board.models import *
import datetime


def _get_post_list(request, item_per_post=15):
    adult_filter = request.GET.get('adult_filter')
    board_filter = request.GET.get('board')
    try:
        page = int(request.GET['page'])
    except:
        page = 1
    board_querystring = '?'
    if board_filter:
        board = Board.objects.filter(id=board_filter)
        if board:
            board = board[0]
        else:
            return ([], [])
        board_querystring = '?board='+board.id
    is_adult = False
    if adult_filter == 'true':
        is_adult = True
    post_count = 0
    if board_filter:
        board_post_notice = BoardPost.objects.filter(board=board_filter, is_notice=True).order_by('-id')
        board_post = BoardPost.objects.filter(board=board_filter).order_by('-id')
        post_count = board.post_count
    else:
        board_post_notice = BoardPost.objects.fiter(is_notice=True).order_by('-id')
        board_post = BoardPost.objects.all().order_by('-id')
        if board_post:
            post_count = board_post[0].id
    last_page = (post_count-1)/item_per_page+1
    if page < 1:
        page = 1
    elif page > last_page:
        page = last_page
    board_post_notice = board_post_notice[:5]
    board_post = board_post[page*item_per_page-item_per_page:page*item_per_page]
    post_list = []
    for board_post in board_post_notice + board_post:
        post = {}
        if board_post.is_notice:
            if board_post.board_content.is_deleted:
                continue
            post['is_notice'] = True
        if board_post.board_content.is_anonymous:
            post['username'] = 'anonymous'
        else:
            post['username'] = board_post.userprofile.user.username
        post_board = {}
        post_board['board_name'] = board_post.board.name
        post_board['querystring'] = '?board='+board_post.board.id
        post['board'] = post_board
        post['title'] = board_post.title
        post['create_time'] = board_post.board_content.created_time
        post['post_id'] = board_post.id
        post['vote'] = board_post.board_content.get_vote()
        if adult_filter == 'true' and board_post.board_content.is_adult:
            post['title'] = 'filtered'
        post_list.append(board_post)
    paginator = []
    if page > 10:
        paging = {}
        paging['page'] = 'prev'
        paging['querystring'] = board_querystring+'&page='+(page-page%10)
        paginator.append(paging)
    for i in range(page-page%10+1,page-page%10+11):
        if i > last_page:
            break
        paging = {}
        paging['page'] = str(i)
        paging['querystring'] = board_querysting+'&page='+i
        paginator.append(paging)
    if i <= last_page-last_page%10:
        paging = {}
        paging['page'] = 'next'
        pagine['querystring'] = board_querystring+'&page='+(last_page-last_page%10+1)
        paginator.append(paging)
    return (post_list, paginator)


def get_board_list():
    board_model_list = Board.objects.all()
    board_list = []
    for board_model in board_model_list:
        board = {}
        board['board_name'] = board_model.name
        board['querystring'] = '?board='+board_model.id
        board_list.append(board)
    return board_list


def get_querystring(request):
    querystring = ''
    board_filter = request.GET.get('board_filter')
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


def get_content(request, post_id):
    board_post = BoardPost.objects.filter(id=post_id)
    if board_post:
        board_post = board_post[0]
    else:
        return (get_post(request, 0), [])
    post = get_post(board_post.board_content.id)
    comment_list = []
    for board_comment in board_post.board_comment.all():
        comment_list.append(get_post(request, board_comment.board_content.id))
    return (post, comment_list)


def get_post(request, content_id):


def _write_post(request,  ):

