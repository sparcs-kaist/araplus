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
from django.contrib import admin
from django.http import HttpResponseRedirect
from settings import BASE_DIR, UPLOAD_DIR, MEDIA_ROOT
import os
import notifications

urlpatterns = [
    # Araplus Apps
    url(r'^board/', include('apps.board.urls')),
    url(r'^grill/', include('apps.grill.urls')),
    url(r'^session/', include('apps.session.urls')),
    url(r'^main/', include('apps.main.urls')),

    url(r'^$', lambda x: HttpResponseRedirect('main/')),
    url(r'^inbox/notifications/', include(notifications.urls)),

    # Admin Page
    url(r'^admin/', include(admin.site.urls)),

    # Media Root
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(BASE_DIR, 'static')}),

    url(r'^upload/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),

    #summernote url
    url(r'^summernote/', include('django_summernote.urls')),

]
