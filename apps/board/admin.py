from django.contrib import admin
from apps.board.models import *

# Register your models here.
admin.site.register(Attachment)
admin.site.register(BoardContent)
admin.site.register(BoardPost)
admin.site.register(BoardComment)
admin.site.register(BoardContentVote)
admin.site.register(Board)
admin.site.register(BoardReport)
admin.site.register(BoardCategory)
admin.site.register(BoardPostIs_read)
admin.site.register(BoardContentVoteAdult)
admin.site.register(BoardContentVotePolitical)
admin.site.register(BoardPostTrace)
admin.site.register(HashTag)
admin.site.register(BoardMember)
