from django.db import models
from apps.session.models import UserProfile

# Create your models here.


class ChannelContent(models.Model):
    content = models.TextField(null=False)
    created_time = models.DateTimeField(auto_now_add=True, null=False)
    is_deleted = models.BooleanField(default=False, null=False)

    def __str__(self):
        if(self.id % 10 == 1):
            return "%dst content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 2):
            return "%dnd content created in %s" % (self.id, self.created_time)
        elif(self.id % 10 == 3):
            return "%drd content created in %s" % (self.id, self.created_time)
        else:
            return "%dth content created in %s" % (self.id, self.created_time)

    def get_vote(self):
        up = 0
        down = 0
        for content_vote in self.channel_content_vote.all():
            if content_vote.is_up:
                up = up+1
            else:
                down = down+1
        vote = {}
        vote['up'] = up
        vote['down'] = down
        return vote


class ChannelAttachment(models.Model):
    file = models.FileField(null=False)
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="attachment",
                                        null=False)


class ChannelComment(models.Model):
    channel_content = models.OneToOneField('ChannelContent',
                                           related_name="channel_comment",
                                           null=False)
    channel_post = models.ForeignKey('ChannelPost',
                                     related_name="channel_comment",
                                     null=False)
    author = models.ForeignKey(UserProfile,
                               related_name="channel_comment")

    def __str__(self):
        created_time = self.channel_content.created_time
        author = self.author.user
        return "created in %s, authored by %s" % (created_time, author)


class ChannelContentVote(models.Model):
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="channel_content_vote",
                                        null=False)
    userprofile = models.ForeignKey(UserProfile,
                                    related_name="channel_content_vote")
    is_up = models.BooleanField(null=False)


class ChannelReport(models.Model):
    reason = models.TextField(null=False)
    content = models.TextField(default='Write something')
    created_time = models.DateTimeField(null=False)
    channel_content = models.ForeignKey('ChannelContent',
                                        related_name="channel_report",
                                        null=False)
    userprofile = models.ForeignKey(UserProfile,
                                    related_name="channel_report")


class Channel(models.Model):
    name = models.CharField(max_length=45, null=False, unique=True)
    channel_url = models.CharField(max_length=45, null=False, unique=True)
    description = models.CharField(max_length=100, null=False)
    author = models.ForeignKey(UserProfile, related_name="channel")
    thumbnail = models.FileField(blank=True, null=False)
    post_count = models.IntegerField(default=0)

    def __unicode__(self):
        name = self.name
        author = self.author
        return u"channel %s, authored by %s" % (name, author)


class ChannelPost(models.Model):
    title = models.CharField(max_length=100, null=False)
    is_notice = models.BooleanField(default=False, null=False)
    channel = models.ForeignKey('Channel',
                                related_name="channel_post",
                                null=False)
    channel_content = models.OneToOneField('ChannelContent', null=False)
    thumbnail = models.FileField(blank=True)

    def __str__(self):
        title = self.title
        created_time = self.channel_content.created_time
        return "title: %s created in %s" % (title, created_time)


class ChannelFavorite(models.Model):
    channel = models.ForeignKey('Channel',
                                related_name="channel_favorite",
                                null=False)
    userprofile = models.ForeignKey(UserProfile,
                                    related_name="channel_favorite")


class ChannelPostScrap(models.Model):
    channel_post = models.ForeignKey('ChannelPost',
                                     related_name="channel_post_scrap",
                                     null=False)
    userprofile = models.ForeignKey(UserProfile,
                                    related_name="channel_post_scrap",
                                    null=False)
