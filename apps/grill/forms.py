# coding: utf-8

from __future__ import unicode_literals
from django import forms
from .models import Grill, GrillComment


class GrillAddForm(forms.ModelForm):

    class Meta:
        model = Grill
        fields = "__all__"
        exclude = ["commented_at", "author"]


class CommentAddForm(forms.ModelForm):

    class Meta:
        model = GrillComment
        fields = ["content"]
