from django.contrib import admin
from .models import Grill, GrillComment, GrillCommentVote

# Register your models here.
admin.site.register(Grill)
admin.site.register(GrillComment)
admin.site.register(GrillCommentVote)
