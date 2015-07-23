from django.db import models
from django.contrib.auth.models import User


MALE = 'M'
FEMALE = 'F'
ETC = 'E'
GENDER = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (ETC, 'etc'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=1, choices=GENDER, default=ETC)
    birthday = models.DateTimeField(blank=True, null=True)

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
