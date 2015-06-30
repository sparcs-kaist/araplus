# -*- coding: utf-8
from django.db import models
from django.core.urlresolvers import reverse_lazy

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
