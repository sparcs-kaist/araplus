# -*- coding: utf-8
from django.db import models
from django.core.urlresolvers import reverse_lazy
import re

# Create your models here.
class Grill(models.Model):
    title = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.IntegerField()
    commented_at = models.DateTimeField(auto_now_add=True)
    contents = models.TextField()

    def get_absolute_url(self):
        return reverse_lazy('view_grill', kwargs = {'grill_id':self.id})


class Comment(models.Model):
    # grill = models.ForeignKey(Grill)
    grill = models.IntegerField()
    author = models.IntegerField()
    contents = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    like_num = models.IntegerField(default=0)
    report_num = models.IntegerField(default=0)

    # return new contents with tags
    # 태그를 <a>로 바꿔서 contents에 저장해둬야하나 아니면
    # 매 번 comment를 부를 때 마다 만들어줘야하나
    # 일단 두 번째 방법으로 구현
    def replace_tags(self):
        # may have some bugs
        return re.sub(r'[\D]?@(?P<target>\d+)(?P<suff>\s|\Z)', r'<a href="#comment_\g<target>">@\g<target></a>\g<suff>', self.contents)
