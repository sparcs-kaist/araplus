from django.contrib import admin
from apps.channel.models import *

# Register your models here.
admin.site.register(ChannelContent)
admin.site.register(ChannelPost)
admin.site.register(ChannelComment)
admin.site.register(ChannelContentVote)
admin.site.register(Channel)
admin.site.register(ChannelReport)
admin.site.register(ChannelCategory)
admin.site.register(ChannelPostIs_read)
admin.site.register(ChannelContentVoteAdult)
admin.site.register(ChannelContentVotePolitical)
admin.site.register(ChannelPostTrace)
admin.site.register(HashTag)
