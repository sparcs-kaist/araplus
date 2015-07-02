from django.db import models
import apps.session.models


class BoardContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(null=False)
    is_deleted = models.BooleanField(default=False, null=False)
    is_anonymous = models.BooleanField(default=False, null=False)


class Attachment(models.Model):
    file = models.FileField(null=False)
    board_content = models.ForeignKey('BoardContent', related_name="attachment", null=False)


class BoardComment(models.Model):
    board_content = models.OneToOneField('BoardContent', related_name="comment", null=False)
    board_post = models.ForeignKey('BoardPost', related_name="comment", null=False)
    # author = models.ForeignKey(session.UserProfile, related_name="board_comment")


class BoardContentVote(models.Model):
    board_content = models.ForeignKey('BoardContent', related_name="content_vote", null=False)
    # userprofile = models.ForeignKey(session.UserProfile, related_name="board_comment_vote")
    is_up = models.BooleanField(null=False)


class BoardReport(models.Model):
    reason = models.TextField(null=False)
    created_time = models.DateTimeField(null=False)
    board_content = models.ForeignKey('BoardContent', related_name="report", null=False)
    # userprofile = models.ForeignKey(session.UserProfile, related_name="board_report")



class Board(models.Model):
    name = models.CharField(max_length=45, null=False)
    description = models.CharField(max_length=100, null=False)


class BoardCategory(models.Model):
    name = models.CharField(max_length=10, null=False)
    board = models.ForeignKey('Board', related_name='category', null=False)


class BoardPostVote(models.Model):
    board_post = models.ForeignKey('BoardPost', related_name='postvote', null=False)
    # userprofile = models.ForeignKey('UserProfile', related_name='voted_board')
    is_up = models.BooleanField(null=False)


class BoardPost(models.Model):
    title = models.CharField(max_length=45, null=False)
    is_notice = models.BooleanField(null=False)
    board = models.ForeignKey('Board', related_name='board', null=False)
    # author = models.ForeignKey('UserProfile', related_name='board_post')
    board_content = models.OneToOneField('BoardContent', null=False)
    board_category = models.ForeignKey('BoardCategory', related_name='category', null=False)

