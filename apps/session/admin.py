from django.contrib import admin
from apps.session.models import UserProfile, Message,\
    GroupMessage, Block, Group


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'points')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'sender', 'receiver')


class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'sender', 'receivers', 'created_time')


class BlockAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('members_list', 'name')

    def members_list(self, obj):
        return ", ".join([str(user) for user in obj.members.all()])

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(GroupMessage, GroupMessageAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Group, GroupAdmin)
