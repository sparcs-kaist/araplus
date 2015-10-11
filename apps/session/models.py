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
    user = models.OneToOneField(User,
                                primary_key=True, related_name='userprofile')
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=1, choices=GENDER, default=ETC)
    birthday = models.DateTimeField(blank=True, null=True)
    signiture = models.CharField(max_length=20)
    nickname = models.TextField(max_length=12)
    points = models.IntegerField(default=0)
    adult_filter = models.BooleanField(default=True)

    def __str__(self):
        return "User %s (%s)'s profile object" % (self.user, self.nickname)


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey('UserProfile', related_name='message_sent')
    receiver = models.ForeignKey('UserProfile',
                                 related_name='message_received')
    created_time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField()

    def __str__(self):
        return "Message from %s to %s at %s" % \
            (self.sender, self.receiver, self.created_time)

    def read(self):
        self.is_read = True
        self.save()


class GroupMessage(models.Model):
    content = models.TextField()
    sender = models.ForeignKey('UserProfile',
                               related_name='group_message_sent')
    receivers = models.ForeignKey('Group',
                                  related_name='group_message_received')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Group Message from %s to %s at %s" % \
            (self.sender, self.receivers, self.created_time)


class Block(models.Model):
    sender = models.ForeignKey('UserProfile',
                               related_name='block_message_from')
    receiver = models.ForeignKey('UserProfile',
                                 related_name='block_message_to')

    def __str__(self):
        return "%s blocked message from %s" % (self.receiver, self.sender)


class Group(models.Model):
    members = models.ManyToManyField(UserProfile, related_name="groups")
    name = models.CharField(max_length=30)

    # second argument(userprofile) can be one object or list of objects
    def add_member(self, userprofile):
        self.members.add(userprofile)
        self.save()

    def remove_member(self, userprofile):
        self.members.remove(userprofile)
        self.save()
