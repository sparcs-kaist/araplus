from django.db import models
import apps.session.models


class BoardContent(models.Model):
	content = models.TextField(null=False)
	created_time = models.DateTimeField(null=False)
	is_deleted = models.BooleanField(default=False, null=False)
	is_anonymous = models.BooleanField(default=False, null=False)


class Attachment(models.Model):
	file = models.FileField(null=False)
	board_content = models.ForeignKey('BoardContent', related_name="attachment")


class BoardComment(models.Model):
	post = models.OneToOneField('BoardPost', related_name="comment")
	# author = models.ForeignKey(session.UserProfile, related_name="board_comment")


class BoardContentVote(models.Model):
	board_content = models.ForeignKey('BoardContent', related_name="content_vote")
	# userprofile = models.ForeignKey(session.UserProfile, related_name="board_comment_vote")
	is_up = models.BooleanField(null=False)


class BoardReport(models.Model):
	reason = models.TextField(null=False)
	created_time = models.DateTimeField(null=False)
	board_content = models.ForeignKey('BoardContent', related_name="report")
	# userprofile = models.ForeignKey(session.UserProfile, related_name="board_report")


class Board(models.Model):
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=100)


class BoardCategory(models.Model):
    name = models.CharField(max_length=10)
    board = models.ForeignKey('Board', related_name='category')


class BoardPostVote(models.Model):
    board_post = models.ForeignKey('BoardPost', related_name='postvote')
    # userprofile = models.ForeignKey('UserProfile', related_name='voted_board')
    is_up = models.BooleanField()


