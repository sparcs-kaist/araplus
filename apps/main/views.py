# -*- coding: utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.board.models import *
from apps.board.backend import (
    _get_post_list,
    _get_querystring,
    _get_content,
    _write_post,
    _delete_post,
    _report,
    _vote,
    _write_comment,
    _create_board,
    _get_post_log,
    _get_comment_log,
    _remove_board,
    _add_member,
    _change_permission,
    _check_valid,
)
import json
from apps.board.forms import *
from django.core.paginator import Paginator

from datetime import datetime, date, timedelta, time

from django.utils import timezone

def home(request):

	todaybest_num = 5
	weekbest_num = 5

	today = datetime.now()
	##todayprelist = BoardContent.objects.filter(created_time__year=today.year , created_time__month=today.month, created_time__day=today.day)
	todayprelist = BoardContent.objects.filter(created_time__range=[today-timedelta(1), today])

	todaylist_num = 0
	todaylist = []
	for tpl in todayprelist:
		try:
			temp_post = tpl.board_post
			todaylist += [tpl]
			todaylist_num = todaylist_num + 1
		except:
			a = 1
	
	if todaybest_num > todaylist_num:
		todaybest_num = todaylist_num
	
	
	today_best_list = []
	maxterm = []
	for j in range(todaybest_num):
		maxup = -1
		tempmax = 0
		for i in range(todaylist_num):
			if todaylist[i].get_vote()['up'] > maxup and not i in maxterm:
				maxup = todaylist[i].get_vote()['up']
				tempmax = i
		maxterm += [tempmax]
		one_article = {}
		one_article['title'] = todaylist[tempmax].board_post.title
		if len(one_article['title']) > 20:
			one_article['title'] = one_article['title'][:20] + "..."
		one_article['vote'] = todaylist[tempmax].get_vote()['up']
		one_article['category'] = todaylist[tempmax].board_post.board.url
		one_article['id'] = todaylist[tempmax].board_post.id
		today_best_list += [one_article]
	
	weekprelist = BoardContent.objects.filter(created_time__range=[today - timedelta(7), today])

	weeklist_num = 0
	weeklist = []
	for tpl in weekprelist:
		try:
			temp_post = tpl.board_post
			weeklist += [tpl]
			weeklist_num = weeklist_num + 1
		except:
			a = 1
	
	if weekbest_num > weeklist_num:
		weekbest_num = weeklist_num

	week_best_list = []
	maxterm = []
	for j in range(weekbest_num):
		maxup = -1
		tempmax = 0
		for i in range(weeklist_num):
			if weeklist[i].get_vote()['up'] > maxup and not i in maxterm:
				maxup = weeklist[i].get_vote()['up']
				tempmax = i
		maxterm += [tempmax]
		one_article = {}
		one_article['title'] = weeklist[tempmax].board_post.title
		if len(one_article['title']) > 20:
			one_article['title'] = one_article['title'][:20] + "..."
		one_article['vote'] = weeklist[tempmax].get_vote()['up']
		one_article['category'] = weeklist[tempmax].board_post.board.url
		one_article['id'] = weeklist[tempmax].board_post.id
		week_best_list += [one_article]

	return render(request,
				'main/main.html',
				{'today_best_list' : today_best_list,
				'week_best_list' : week_best_list,
					})


def credit(request):
    return render(request, 'main/credit.html')
