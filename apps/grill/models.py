# -*- coding: utf-8
from django.db import models

# Create your models here.
class Grill(models.Model):
	title = models.CharField(max_length=80)
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.IntegerField()
	commented_at = models.DateTimeField()
	contents = models.TextField()

class Comment(models.Model):
	# grill = models.ForeignKey(Grill)
	grill = models.IntegerField()
	author = models.IntegerField()
	contents = models.TextField(max_length=280)
	created_at = models.DateTimeField(auto_now_add=True)
	like_num = models.IntegerField(default=0)
	report_num = models.IntegerField(default=0)
