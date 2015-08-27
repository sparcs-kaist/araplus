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
    url(r'^create/$', 'apps.channel.views.create'),
    url(r'^([A-z0-9]*)/$', 'apps.channel.views.list'),

    url(r'^([A-z0-9]*)/write/$', 'apps.channel.views.write_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/write/$',
        'apps.channel.views.write_comment'),

    url(r'^([A-z0-9]*)/([1-9][0-9]*)/$', 'apps.channel.views.read_post'),

    url(r'^([A-z0-9]*)/modify/$', 'apps.channel.views.modify_channel'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/modify/$', 'apps.channel.views.modify_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/modify/$',
        'apps.channel.views.modify_comment'),

    url(r'^([A-z0-9]*)/delete/$', 'apps.channel.views.delete_channel'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/delete/$', 'apps.channel.views.delete_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/delete/$',
        'apps.channel.views.delete_comment'),

    url(r'^([A-z0-9]*)/([1-9][0-9]*)/log/$', 'apps.channel.views.log_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/log/$',
        'apps.channel.views.log_comment'),

    url(r'^([A-z0-9]*)/([1-9][0-9]*)/mark19/$', 'apps.channel.views.mark19_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/mark19/$',
        'apps.channel.views.mark19_comment'),

    url(r'^([A-z0-9]*)/([1-9][0-9]*)/vote/$', 'apps.channel.views.vote_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/vote/$',
        'apps.channel.views.vote_comment'),

    url(r'^([A-z0-9]*)/([1-9][0-9]*)/report/$', 'apps.channel.views.report_post'),
    url(r'^([A-z0-9]*)/([1-9][0-9]*)/([1-9][0-9]*)/report/$',
        'apps.channel.views.report_comment'),
]
