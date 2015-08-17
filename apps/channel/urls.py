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
    url(r'^$', 'apps.channel.views.home'),
    url(r'^([A-z]*)/$', 'apps.channel.views.post_list', name='post_list'),
    url(r'^([A-z]*)/post/$', 'apps.channel.views.post_write'),
    url(r'^([A-z]*)/([1-9][0-9]*)/$', 'apps.channel.views.post_read'),
    url(r'^[A-z]*/([1-9][0-9]*)/modify/$', 'apps.channel.views.post_modify'),
    url(r'^([A-z]*)/([1-9][0-9]*)/post-log/$',
        'apps.channel.views.post_modify_log'),
    url(r'^([A-z]*)/([1-9][0-9]*)/comment-log/$',
        'apps.channel.views.comment_modify_log'),
    url(r'^[A-z]*/([1-9][0-9]*)/comment/$', 'apps.channel.views.comment_write'),
    url(r'^[A-z]*/([1-9][0-9]*)/comment_mod/$',
        'apps.channel.views.comment_modify'),
    url(r'^[A-z]*/[1-9][0-9]*/delete/$', 'apps.channel.views.delete'),
    url(r'^[A-z]*/[1-9][0-9]*/vote/$', 'apps.channel.views.content_vote'),
    url(r'^[A-z]*/[1-9][0-9]*/report/$', 'apps.channel.views.report'),
    url(r'^[A-z]*/([1-9][0-9]*)/trace/$', 'apps.channel.views.trace'),
    url(r'^[A-z]*/trace/$', 'apps.channel.views.trace_list'),
]
