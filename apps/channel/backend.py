# -*- coding: utf-8
from apps.channel.models import Channel


def _make_channel(request):
    user_profile = request.user.userprofile
    name = request.POST.get('name', '')
    description = request.POST.get('description', '')
    thumbnail = request.POST.get('thumbnail', '')
    channel = Channel()
    channel.name = name
    channel.description = description
    channel.author = user_profile
    channel.thumbnail = thumbnail
    channel.save()
    return channel.id
