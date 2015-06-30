# coding: utf-8

from __future__ import unicode_literals
from django import forms
from .models import Comment

class CommentAddForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ["contents"]