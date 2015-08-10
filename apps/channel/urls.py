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
from django.conf.urls import url
# from django.contrib import admin

urlpatterns = [
    url(r'^$', 'apps.channel.views.main'),
    url(r'^register_channel/$', 'apps.channel.views.register_channel'),
    url(r'^(?P<channel_url>[A-z0-9]*)/$',
        'apps.channel.views.view_channel'),
    url(r'^(?P<channel_url>[A-z0-9]*)/write/$',
        'apps.channel.views.write_post'),
    url(r'^(?P<channel_url>[A-z0-9]*)/(?P<channel_post_id>[1-9][0-9]*)/$',
        'apps.channel.views.read_post'),
    url(r'^(?P<channel_url>[A-z0-9]*)/(?P<channel_post_id>[1-9][0-9]*)/edit/$',
        'apps.channel.views.edit_post'),
    url(r'^(?P<channel_url>[A-z0-9]*)/(?P<channel_post_id>[1-9][0-9]*)/delete$',
        'apps.channel.views.delete_post'),
    url(r'^(?P<channel_url>[A-z0-9]*)/(?P<channel_post_id>[1-9][0-9]*)/rating/(?P<rating>[0-9]+)$', 'apps.channel.views.give_rating'),
    # url(r'^([^/]+)/([1-9][0-9]*)/comment/$', 'apps.channel.views.comment'),
    # url(r'^([^/]+)/([1-9][0-9]*)/comment_edit/$',
    #     'apps.channel.views.edit_comment'),
    # url(r'^up/$', 'apps.channel.views.up'),
    # url(r'^down/$', 'apps.channel.views.down'),
    # url(r'^delete/$', 'apps.channel.views.delete_channel'),
    # url(r'^report/$', 'apps.channel.views.report'),
]
