# -*- coding: utf-8
from django.db import models
from django.core.urlresolvers import reverse_lazy
from apps.session.models import UserProfile
import re


class Grill(models.Model):
    title = models.CharField(max_length=80)
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile)
    updated_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def get_absolute_url(self):
        return reverse_lazy('view_grill', kwargs={'grill_id': self.id})


class GrillComment(models.Model):

    def save(self, *args, **kwargs):
        no = GrillComment.objects.filter(grill=self.grill).count()
        if no:
            self.order = no + 1
        else:
            self.order = 1
        super(GrillComment, self).save(*args, **kwargs)

    grill = models.ForeignKey(Grill)
    author = models.ForeignKey(UserProfile)
    content = models.TextField(max_length=140)
    created_time = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(
        db_index=True)

    def to_json(self):
        return dict(
            author=self.author.id,
            content=self.replace_tags(),
            created_time=self.created_time.isoformat(),
            order=self.order)

    # return new contents with tags
    # 태그를 <a>로 바꿔서 contents에 저장해둬야하나 아니면
    # 매 번 comment를 부를 때 마다 만들어줘야하나
    # 일단 두 번째 방법으로 구현
    def replace_tags(self):
        return re.sub(r'@(?P<target>\d+)',
                      '<a href="#comment_\g<target>">@\g<target></a>',
                      self.content)


class GrillCommentVote(models.Model):
    grill_comment = models.ForeignKey(GrillComment, null=False)
    userprofile = models.ForeignKey(UserProfile)
    is_up = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
