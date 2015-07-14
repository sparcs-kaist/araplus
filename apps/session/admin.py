from django.contrib import admin
from apps.session.models import UserProfile, Message, Block


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'points')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'sender', 'receiver')


class BlockAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Block, BlockAdmin)
