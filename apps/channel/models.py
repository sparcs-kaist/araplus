# -*- coding: utf-8 -*-
from django.db import models
import apps.session.models
from araplus.settings import UPLOAD_DIR
import json
import re
import cgi
hashtag_regex = re.compile(ur'(^|(?<=\s))#(?P<target>\w+)', re.UNICODE)


class ChannelContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, null=False)
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
        for content_vote in self.channel_content_vote.all():
            if content_vote.is_up:
                up = up + 1
            else:
                down = down + 1
        vote = {}
        vote['up'] = up
        vote['down'] = down
        return vote

    def replace_content_tags(self):
        result = cgi.escape(self.content)
        result = result.replace("\n", "<br />")
        result = re.sub(r'@(?P<target>\d+)',
                        '<a title="comment_\g<target>" class="comment_preview" href="#comment_order_\g<target>">@\g<target></a>', result)
        return hashtag_regex.sub(
            '\1<a href="../?tag=\g<target>">#\g<target></a>',
            result)

    def get_hashtags(self):
        return [tag[1] for tag in hashtag_regex.findall(self.content)]


class Attachment(models.Model):
    file = models.FileField(null=False, upload_to=UPLOAD_DIR)
    channel_content = models.ForeignKey('ChannelContent',
                                      related_name="attachment",
                                      null=False)


class ChannelComment(models.Model):
    channel_content = models.OneToOneField('ChannelContent',
                                         related_name="channel_comment",
                                         null=False)
    channel_post = models.ForeignKey('ChannelPost',
                                   related_name="channel_comment",
                                   null=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name="channel_comment")

    def __str__(self):
        created_time = self.channel_content.created_time
        author = self.author.user
        return "created in %s, authored by %s" % (created_time, author)


class ChannelContentVote(models.Model):
    channel_content = models.ForeignKey('ChannelContent',
                                      related_name="channel_content_vote",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_content_vote")
    is_up = models.BooleanField(null=False)


class ChannelContentVoteAdult(models.Model):
    channel_content = models.ForeignKey('ChannelContent',
                                      related_name="channel_content_vote_adult",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_content_vote_adult")


class ChannelContentVotePolitical(models.Model):
    channel_content = models.ForeignKey(
        'ChannelContent',
        related_name="channel_content_vote_political",
        null=False)
    userprofile = models.ForeignKey(
        'session.UserProfile',
        related_name="channel_content_vote_political")


class ChannelReport(models.Model):
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
    channel_content = models.ForeignKey('ChannelContent',
                                      related_name="channel_report",
                                      null=False)
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_report")


class Channel(models.Model):
    kor_name = models.CharField(max_length=45, null=False, unique=True)
    eng_name = models.CharField(max_length=45, null=False, unique=True)
    url = models.CharField(max_length=45, null=False, unique=True)
    description = models.CharField(max_length=100, null=False)
    admin = models.ForeignKey('session.UserProfile',
                              related_name="channel",
                              null=False)
    thumbnail = models.TextField(null=False) # Should be changed
    is_official = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.kor_name


class ChannelMember(models.Model):
    channel = models.ForeignKey('channel',
                              related_name='channel_member',
                              null=False)
    member = models.ForeignKey('session.userprofile',
                               related_name='channel_member',
                               null=False)

    class Meta:
        unique_together = ('channel', 'member',)


class ChannelPost(models.Model):
    title = models.CharField(max_length=45, null=False)
    is_notice = models.BooleanField(default=False, null=False, db_index=True)
    is_best = models.BooleanField(default=False, db_index=True)
    channel = models.ForeignKey('Channel',
                              related_name='channel',
                              null=False,
                              db_index=True)
    author = models.ForeignKey('session.UserProfile',
                               related_name='channel_post')
    channel_content = models.OneToOneField('ChannelContent', null=False,
                                         related_name='channel_post')
    modify_log = models.TextField(default='[]')

    class Meta:
        ordering = ['-id']

    def get_is_read(self, request):
        try:
            return self.channel_post_is_read.get(
                userprofile=request.user.userprofile)
        except:
            return None

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __unicode__(self):
        title = self.title
        created_time = self.channel_content.created_time
        author = self.author.user
        return u"title: %s created in %s, authored by %s" % (title,
                                                             created_time,
                                                             author)


class ChannelPostIs_read(models.Model):
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name='channel_post_is_read')
    channel_post = models.ForeignKey('ChannelPost',
                                   related_name='channel_post_is_read')
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('userprofile', 'channel_post',)


class ChannelPostTrace(models.Model):
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name='channel_post_trace')
    channel_post = models.ForeignKey('ChannelPost',
                                   related_name='channel_post_trace')
    is_trace = models.BooleanField(default=True)
    is_notified = models.BooleanField(default=False)
    last_created = models.DateTimeField(auto_now=True)


class HashTag(models.Model):
    tag_name = models.TextField(null=False, db_index=True)
    channel_post = models.ForeignKey('ChannelPost',
                                   related_name="hashtag",
                                   null=False)
