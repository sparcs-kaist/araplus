from django.contrib import admin
from apps.channel.models import *

# Register your models here.
admin.site.register(Channel)
admin.site.register(ChannelContent)
admin.site.register(ChannelPostVote)
admin.site.register(ChannelCommentVote)
admin.site.register(ChannelMarkAdult)
admin.site.register(ChannelReport)
admin.site.register(ChannelComment)
admin.site.register(ChannelPost)
admin.site.register(ChannelPostIsRead)
admin.site.register(ChannelPostTrace)
admin.site.register(HashTag)
admin.site.register(Attachment)
