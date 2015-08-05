# -*- coding: utf-8 -*-
from django.db import models
import apps.session.models
import json


class BoardContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, null=False)
    is_anonymous = models.TextField(default=None, null=True)
    is_adult = models.BooleanField(default=False, null=False)
    modify_log = models.TextField(default='[]')

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __str__(self):
        if(self.id % 10 == 1):
            return "%dst content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 2):
            return "%dnd content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 3):
            return "%dnd content created in %s" % (self.id, self.created_time)
        else:
            return "%dth content created in %s" % (self.id, self.created_time)

    def get_vote(self):
        up = 0
        down = 0
        for content_vote in self.board_content_vote.all():
            if content_vote.is_up:
                up = up+1
            else:
                down = down+1
        vote = {}
        vote['up'] = up
        vote['down'] = down
        return vote


class Attachment(models.Model):
    file = models.FileField(null=False)
    board_content = models.ForeignKey('BoardContent',
                                      related_name="attachment",
                                      null=False)


class BoardComment(models.Model):
    board_content = models.OneToOneField('BoardContent',
                                         related_name="board_comment",
                                         null=False)
    board_post = models.ForeignKey('BoardPost',
                                   related_name="board_comment",
                                   null=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name="board_comment")

    def __str__(self):
        created_time = self.board_content.created_time
        author = self.author.user
        return "created in %s, authored by %s" % (created_time, author)


class BoardContentVote(models.Model):
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_content_vote",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_content_vote")
    is_up = models.BooleanField(null=False)


class BoardContentVoteAdult(models.Model):
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_content_vote_adult",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_content_vote_adult")


class BoardContentVotePolitical(models.Model):
    board_content = models.ForeignKey(
        'BoardContent',
        related_name="board_content_vote_political",
        null=False)
    userprofile = models.ForeignKey(
        'session.UserProfile',
        related_name="board_content_vote_political")


class BoardReport(models.Model):
    Reason1 = u'이유1'
    Reason2 = u'이유2'
    Etc = u'기타'
    Reason_Choice = (
        (Reason1, u'이유1'),
        (Reason2, u'이유2'),
        (Etc, u'기타'))
    reason = models.CharField(max_length=4,
                              choices=Reason_Choice,
                              default=Etc)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    board_content = models.ForeignKey('BoardContent',
                                      related_name="board_report",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="board_report")


class Board(models.Model):
    kor_name = models.CharField(max_length=45, null=False, unique=True)
    eng_name = models.CharField(max_length=45, null=False, unique=True)
    url = models.CharField(max_length=45, null=False, unique=True)
    description = models.CharField(max_length=100, null=False)

    def __unicode__(self):
        return self.kor_name


class BoardCategory(models.Model):
    name = models.CharField(max_length=10, null=False)
    board = models.ForeignKey('Board',
                              related_name='board_category',
                              null=False)


class BoardPost(models.Model):
    title = models.CharField(max_length=45, null=False)
    is_notice = models.BooleanField(default=False, null=False, db_index=True)
    is_best = models.BooleanField(default=False, db_index=True)
    board = models.ForeignKey('Board',
                              related_name='board',
                              null=False,
                              db_index=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name='board_post')
    board_content = models.OneToOneField('BoardContent', null=False,
                                         related_name='board_post')
    board_category = models.ForeignKey('BoardCategory',
                                       related_name='board_post',
                                       null=True,
                                       blank=True)
    modify_log = models.TextField(default='[]')

    class Meta:
        ordering = ['-id']

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __unicode__(self):
        title = self.title
        created_time = self.board_content.created_time
        author = self.author.user
        return u"title: %s created in %s, authored by %s" % (title,
                                                             created_time,
                                                             author)


class BoardPostIs_read(models.Model):
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name='board_post_is_read')
    board_post = models.ForeignKey('BoardPost',
                                   related_name='board_post_is_read')
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('userprofile', 'board_post',)
