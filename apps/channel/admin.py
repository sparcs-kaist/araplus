from django.contrib import admin
from apps.channel.models import (
    Channel,
    ChannelPost,
    ChannelContent,
)

# Register your models here.


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'author',
                    'thumbnail', 'post_count')
    list_filter = ('author',)


admin.site.register(Channel, ChannelAdmin)


class ChannelPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_notice', 'channel',
                    'channel_content', 'thumbnail')
    list_filter = ('title', 'channel', 'channel_content')


admin.site.register(ChannelPost, ChannelPostAdmin)


class ChannelContentAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_time', 'is_deleted')
    list_filter = ('is_deleted',)


admin.site.register(ChannelContent, ChannelContentAdmin)
