from django.contrib import admin
from apps.session.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')


admin.site.register(UserProfile, UserProfileAdmin)
