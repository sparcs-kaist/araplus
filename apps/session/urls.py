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
    url(r'^$', 'apps.session.views.main'),
    url(r'^login/$', 'apps.session.views.user_login'),
    url(r'^login/callback/$', 'apps.session.views.user_login_callback'),
    url(r'^logout/$', 'apps.session.views.user_logout'),
    url(r'^register/$', 'apps.session.views.user_register'),
    url(r'^nickname-check/$', 'apps.session.views.nickname_check'),
    url(r'^message/', include('apps.session.message.urls')),
    url(r'^group/', include('apps.session.group.urls')),
]
