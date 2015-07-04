from django.contrib import admin
from apps.board.models import *

# Register your models here.
admin.site.register(BoardContent)
admin.site.register(BoardPost)
admin.site.register(BoardComment)
admin.site.register(BoardContentVote)
