from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True, related_name='userprofile')
    nickname = models.TextField(max_length=12)
    points = models.IntegerField(default=0)

    def __str__(self):
        return "User %s (%s)'s profile object" % (self.user, self.nickname)


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey('UserProfile', related_name='message_sent')
    receiver = models.ForeignKey('UserProfile',
                                 related_name='message_received')
    created_time = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField()

    def __str__(self):
        return "Message from %s to %s at %s" % \
            (self.sender, self.receiver, self.created_time)

    def read(self):
        self.is_read = True
        self.save()


class Block(models.Model):
    sender = models.ForeignKey('UserProfile',
                               related_name='block_message_from')
    receiver = models.ForeignKey('UserProfile',
                                 related_name='block_message_to')

    def __str__(self):
        return "%s blocked message from %s" % (self.receiver, self.sender)
