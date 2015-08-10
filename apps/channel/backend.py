# -*- coding: utf-8
from apps.channel.models import Channel, ChannelContentVote


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


def _give_rating_backend(channel_content, user_profile, rating):
    rating = int(rating)
    if 1 <= rating and rating <= 10:
        votes = ChannelContentVote.objects.filter(channel_content=channel_content,
                                                  userprofile=user_profile)
        for vote in votes:
            vote.delete()
        vote = ChannelContentVote(channel_content=channel_content,
                                  userprofile=user_profile,
                                  rating=rating)
        vote.save()
