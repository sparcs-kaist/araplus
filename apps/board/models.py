from django.db import models
import apps.session.models


class BoardContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(null=False)
    is_deleted = models.BooleanField(default=False, null=False)
    is_anonymous = models.BooleanField(default=False, null=False)
    is_adult = models.BooleanField(default=False, null=False)

    def __str__(self):
        if(self.id%10==1):
            return "%dst content created in %s" %(self.id, self.created_time)
        elif(self.id%10==2):
            return "%dnd content created in %s" %(self.id, self.created_time)
        elif(self.id%10==3):
            return "%dnd content created in %s" %(self.id, self.created_time)
        else:
            return "%dth content created in %s" %(self.id, self.created_time)

    def get_vote(self):
        up = 0
        down = 0
        for content_vote in self.content_vote.all():
            if content_vote.is_up:
                up=up+1
            else:
                down= down+1
        vote = {}
        vote['up']=up
        vote['down']=down
        return vote


class Attachment(models.Model):
    file = models.FileField(null=False)
    board_content = models.ForeignKey('BoardContent', related_name="attachment", null=False)


class BoardComment(models.Model):
    board_content = models.OneToOneField('BoardContent', related_name="comment", null=False)
    board_post = models.ForeignKey('BoardPost', related_name="comment", null=False)
    author = models.ForeignKey('session.UserProfile', related_name="board_comment")

    def __str__(self):
        return "created in %s, authored by %s" %(self.board_content.created_time, self.author.user)


class BoardContentVote(models.Model):
    board_content = models.ForeignKey('BoardContent', related_name="content_vote", null=False)
    userprofile = models.ForeignKey('session.UserProfile', related_name="board_comment_vote")
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
    is_notice = models.BooleanField(default=False,null=False)
    # board = models.ForeignKey('Board', related_name='board_post', null=False)
    author = models.ForeignKey('session.UserProfile', related_name='board_post')
    board_content = models.OneToOneField('BoardContent', null=False)
    # board_category = models.ForeignKey('BoardCategory', related_name='category', null=False)

    def __str__(self):
        return "title: %s created in %s , authored by %s" %(self.title, self.board_content.created_time, self.author.user)
