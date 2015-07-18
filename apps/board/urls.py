"""araplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', 'apps.board.views.post_list', name='post_list'),
    url(r'^post/$', 'apps.board.views.post_write'),
    url(r'^([1-9][0-9]*)/$', 'apps.board.views.post_read'),
    url(r'^([1-9][0-9]*)/modify/$', 'apps.board.views.post_modify'),
    url(r'^([1-9][0-9]*)/comment/$', 'apps.board.views.comment_write'),
    url(r'^([1-9][0-9]*)/comment_mod/$', 'apps.board.views.comment_modify'),
    url(r'^up/$', 'apps.board.views.up'),
    url(r'^down/$', 'apps.board.views.down'),
    url(r'^delete/$','apps.board.views.delete'),
    url(r'^vote_adult/$', 'apps.board.views.vote_adult'),
    url(r'^vote_political/$', 'apps.board.views.vote_political'),
    url(r'^report/$', 'apps.board.views.report'),
]
