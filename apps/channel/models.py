# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Avg
from araplus.settings import UPLOAD_DIR
import json
import re
import cgi
hashtag_regex = re.compile(ur'(^|(?<=\s))#(?P<target>\w+)', re.UNICODE)
numtag_regex = re.compile(r'@(?P<target>\d+)')

class Channel(models.Model):
    kor_name = models.CharField(max_length=45, unique=True)
    eng_name = models.CharField(max_length=45, unique=True)
    url = models.CharField(max_length=45, unique=True)
    description = models.TextField()
    admin = models.ForeignKey('session.UserProfile',
                              related_name="channel")
    thumbnail = models.ImageField(null=True, blank=True, upload_to=UPLOAD_DIR)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.kor_name


class ChannelContent(models.Model):
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_adult = models.BooleanField(default=False)
    modify_log = models.TextField(default='[]')

    def is_mark19(self, userprofile):
        return ChannelMarkAdult.objects.filter(channel_content=self, userprofile=userprofile).count() == 1

    def set_log(self, log):
        self.modify_log = json.dumps(log)

    def get_log(self):
        return json.loads(self.modify_log)

    def __unicode__(self):
        if(self.id % 10 == 1):
            return "%dst content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 2):
            return "%dnd content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 3):
            return "%dnd content created in %s" % (self.id, self.created_time)
        else:
            return "%dth content created in %s" % (self.id, self.created_time)

    def replace_content_tags(self):
        result = cgi.escape(self.content)
        result = result.replace("\n", "<br/>")
        result = numtag_regex.sub('<a class="numtag" data-order="\g<target>">@\g<target></a>', result)
        return hashtag_regex.sub(
            '\1<a href="../?tag=\g<target>">#\g<target></a>',
            result)

    def get_hashtags(self):
        return [tag[1] for tag in hashtag_regex.findall(self.content)]

    def get_numtags(self):
        return [tag[1] for tag in numtag_regex.findall(self.content)]


class Attachment(models.Model):
    file = models.FileField(upload_to=UPLOAD_DIR)
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="attachment")


class ChannelPostVote(models.Model):
    channel_post = models.ForeignKey('ChannelPost',
                                     related_name="channel_post_vote")
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_post_vote")
    rating = models.IntegerField()


class ChannelCommentVote(models.Model):
    channel_comment = models.ForeignKey('ChannelComment',
                                        related_name="channel_comment_vote")
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_comment_vote")
    is_up = models.BooleanField()


class ChannelMarkAdult(models.Model):
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="channel_mark_adult")
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_mark_adult")


class ChannelReport(models.Model):
    REASON1 = 'R1'
    REASON2 = 'R2'
    ETC = 'ETC'
    REASON_CHOICE = (
        (REASON1, u'이유1'),
        (REASON2, u'이유2'),
        (ETC, u'기타'))
    reason = models.CharField(max_length=3,
                              choices=REASON_CHOICE,
                              default=ETC)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="channel_report")
    userprofile = models.ForeignKey('session.UserProfile',
                                    related_name="channel_report")


class ChannelComment(models.Model):
    channel_content = models.OneToOneField('ChannelContent',
                                           related_name="channel_comment")
    channel_post = models.ForeignKey('ChannelPost',
                                     related_name="channel_comment")
    author = models.ForeignKey('session.UserProfile',
                               related_name="channel_comment")
    order = models.IntegerField(default=-1)
    
    def get_vote(self):
        votes = ChannelCommentVote.objects.filter(channel_comment=self)
        return votes.filter(is_up=True).count(), votes.filter(is_up=False).count()

    def get_my_vote(self, userprofile):
        vote = {'is_up': False, 'is_down': False}
        try:
            vote_obj = ChannelCommentVote.objects.get(userprofile=userprofile, channel_comment=self)
            if vote_obj.is_up:
                vote['is_up'] = True
            else:
                vote['is_down'] = True
        except:
            pass
        return vote

    def save(self, *args, **kwargs):
        if self.order == -1:
            no = ChannelComment.objects.filter(channel_post=self.channel_post).count()
            if not no:
                no = 0
            self.order = no + 1
        super(ChannelComment, self).save(*args, **kwargs)

    def __unicode__(self):
        created_time = self.channel_content.created_time
        author = self.author.user
        return "created in %s, authored by %s" % (created_time, author)


class ChannelPost(models.Model):
    title = models.CharField(max_length=45)
    is_notice = models.BooleanField(default=False, db_index=True)
    channel = models.ForeignKey('Channel',
                                related_name='channel',
                                db_index=True)
    order = models.IntegerField(default=-1)
    author = models.ForeignKey('session.UserProfile',
                               related_name='channel_post')
    channel_content = models.OneToOneField('ChannelContent',
                                           related_name='channel_post')
    modify_log = models.TextField(default='[]')

    class Meta:
        ordering = ['-id']
    
    def get_rating(self):
        ratings = ChannelPostVote.objects.filter(channel_post=self)
        value = ratings.aggregate(Avg('rating')).values()[0]
        if value is None:
            return 0
        return value
    
    def get_my_rating(self, userprofile):
        try:
            return ChannelPostVote.objects.get(channel_post=self,
                    userprofile=userprofile).rating
        except:
            return 0

    def get_best_comments(self):
        comments = ChannelComment.objects.filter(channel_post=self)
        best_comments = list(reversed(sorted(
            filter(lambda x: x.get_vote()[0] > 5, comments),
            key=lambda x: x.get_vote()[0] - x.get_vote()[1])))
 
        if len(best_comments) > 3:
            return best_comments[:3]
        return best_comments

    def save(self, *args, **kwargs):
        if self.order == -1:
            no = ChannelPost.objects.filter(channel=self.channel).count()
            if not no:
                no = 0
            self.order = no + 1
        super(ChannelPost, self).save(*args, **kwargs)

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


class ChannelPostIsRead(models.Model):
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
    tag_name = models.TextField(db_index=True)
    channel_post = models.ForeignKey('ChannelPost',
                                     related_name="hashtag")
