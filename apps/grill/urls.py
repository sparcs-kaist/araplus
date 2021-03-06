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
    url(r'^$', 'apps.grill.views.home'),
    url(r'^(?P<grill_id>\d+)/refresh_comment/$',
        'apps.grill.views.refresh_comment', name='refresh_comment'),
    url(r'^add_grill/',
        'apps.grill.views.add_grill', name='add_grill'),
    url(r'^(?P<grill_id>\d+)$',
        'apps.grill.views.view_grill', name='view_grill'),
    url(r'^(?P<grill_id>\d+)/add_comment/$',
        'apps.grill.views.add_comment', name='add_comment'),
    url(r'^(?P<grill_id>\d+)/vote_comment/$',
        'apps.grill.views.vote_comment', name='vote_comment'),
]
